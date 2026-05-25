"""
CasaTua quiz backend.

Single endpoint POST /api/quiz that:
- accepts the 12 quiz answers
- calls Claude with a forced tool_use schema (structured output)
- enriches each product with a verified URL from stores.STORE_URLS
- returns the structured result to the frontend

Structured tool_use eliminates JSON parsing failures: Claude fills a
declared schema and the SDK returns it as a dict, with no truncation-
related JSONDecodeError or markdown-fence stripping needed.
"""

import logging
import os
import time
from collections import defaultdict, deque
from pathlib import Path

import anthropic
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, conlist

from prompt import PROFILE_TOOL, QUESTIONS, build_user_message
from stores import STORE_URLS, resolve_url

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("casatua")

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-haiku-4-5")
# 4000 is comfortable for the full 6-store profile (~2500-3500 tokens typical).
MAX_TOKENS = max(int(os.environ.get("MAX_TOKENS", "4000")), 3000)
# Per-attempt Claude timeout. With up to 2 retries on transient errors, the
# realistic worst case is around 20-25s (two fast 529 responses + backoff +
# a successful third attempt). Frontend AbortController allows 60s.
CLAUDE_TIMEOUT_S = 30.0
TOOL_NAME = PROFILE_TOOL["name"]

# Anthropic statuses that are worth retrying. 529 (overloaded) is the main
# one we see in production — Anthropic recovers within seconds. 502/503/504/
# 520 are transient gateway issues.
# 429 (rate limit) and 4xx client errors are intentionally not retried.
_RETRYABLE_STATUSES = frozenset({502, 503, 504, 520, 529})
_MAX_RETRIES = 2  # total attempts = _MAX_RETRIES + 1
_BACKOFF_BASE_S = 1.0  # backoff sequence: 1s, 2s

if not ANTHROPIC_API_KEY:
    log.warning("ANTHROPIC_API_KEY is not set. /api/quiz will return 500 until configured.")

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None

app = FastAPI(title="CasaTua Quiz API")


# Simple in-memory rate limit: 5 requests per IP per minute.
_RATE: dict[str, deque] = defaultdict(deque)
_RATE_WINDOW_S = 60
_RATE_MAX = 5


def _rate_limited(ip: str) -> bool:
    now = time.time()
    bucket = _RATE[ip]
    while bucket and now - bucket[0] > _RATE_WINDOW_S:
        bucket.popleft()
    if len(bucket) >= _RATE_MAX:
        return True
    bucket.append(now)
    return False


class QuizRequest(BaseModel):
    answers: conlist(int, min_length=len(QUESTIONS), max_length=len(QUESTIONS)) = Field(
        ..., description="One integer 0..3 per question, in order"
    )


@app.get("/api/health")
def health():
    return {
        "ok": True,
        "model": ANTHROPIC_MODEL,
        "questions": len(QUESTIONS),
        "max_tokens": MAX_TOKENS,
        "claude_timeout_s": CLAUDE_TIMEOUT_S,
        "max_retries": _MAX_RETRIES,
        "key_configured": bool(ANTHROPIC_API_KEY),
    }


@app.post("/api/quiz")
def quiz(req: QuizRequest, request: Request):
    if client is None:
        raise HTTPException(status_code=500, detail="Server non configurato: ANTHROPIC_API_KEY mancante.")

    for i, a in enumerate(req.answers):
        if not (0 <= a <= 3):
            raise HTTPException(status_code=400, detail=f"Risposta non valida per Q{i + 1}.")

    ip = request.client.host if request.client else "unknown"
    if _rate_limited(ip):
        raise HTTPException(status_code=429, detail="Troppe richieste. Riprova fra un minuto.")

    user_message = build_user_message(req.answers)

    try:
        message = _call_claude_with_retry(
            model=ANTHROPIC_MODEL,
            max_tokens=MAX_TOKENS,
            timeout=CLAUDE_TIMEOUT_S,
            tools=[PROFILE_TOOL],
            tool_choice={"type": "tool", "name": TOOL_NAME},
            messages=[{"role": "user", "content": user_message}],
        )
    except anthropic.APITimeoutError:
        log.warning("Claude API timeout after %ss", CLAUDE_TIMEOUT_S)
        raise HTTPException(status_code=504, detail="Claude ha impiegato troppo tempo. Riprova fra qualche istante.")
    except anthropic.RateLimitError:
        log.warning("Anthropic rate limit hit")
        raise HTTPException(status_code=429, detail="Limite di richieste raggiunto. Riprova fra un minuto.")
    except anthropic.APIStatusError as e:
        status = getattr(e, "status_code", "?")
        log.exception("Anthropic API error status=%s after retries", status)
        if status == 529:
            detail = "I server di Claude sono temporaneamente sovraccarichi. Riprova fra qualche istante."
        else:
            detail = f"Errore Anthropic ({status}). Riprova fra qualche istante."
        raise HTTPException(status_code=502, detail=detail)
    except Exception:
        log.exception("Unexpected error calling Anthropic")
        raise HTTPException(status_code=500, detail="Errore interno. Riprova.")

    result = _extract_tool_input(message)
    result = _enrich_with_urls(result)
    return JSONResponse(result)


def _call_claude_with_retry(**kwargs):
    """Call Claude with automatic retry on transient upstream errors.

    Retries on 529 (overloaded) and other transient gateway statuses defined
    in _RETRYABLE_STATUSES. Backoff is 1s then 2s. Non-transient errors and
    timeouts are re-raised immediately so the caller can map them to a clear
    user message. After _MAX_RETRIES extra attempts the last error bubbles up.
    """
    for attempt in range(_MAX_RETRIES + 1):
        try:
            return client.messages.create(**kwargs)
        except anthropic.APIStatusError as e:
            status = getattr(e, "status_code", None)
            if status not in _RETRYABLE_STATUSES or attempt == _MAX_RETRIES:
                raise
            wait_s = _BACKOFF_BASE_S * (2 ** attempt)
            log.warning(
                "Anthropic %s, retrying in %.1fs (attempt %d/%d)",
                status, wait_s, attempt + 2, _MAX_RETRIES + 1,
            )
            time.sleep(wait_s)


def _extract_tool_input(message) -> dict:
    """Pull the structured input out of Claude's tool_use block.

    With tool_choice forced, Claude is guaranteed to emit a tool_use block.
    The only realistic failure here is hitting max_tokens before the tool
    call completes — in which case `input` may be missing required fields.
    """
    tool_block = None
    for block in message.content:
        if getattr(block, "type", None) == "tool_use" and block.name == TOOL_NAME:
            tool_block = block
            break

    if tool_block is None:
        # Should not happen with tool_choice forced.
        log.error(
            "No tool_use block in response. stop_reason=%s, content=%r",
            getattr(message, "stop_reason", None),
            message.content,
        )
        raise HTTPException(
            status_code=502,
            detail="Claude non ha completato il profilo. Riprova.",
        )

    if message.stop_reason == "max_tokens":
        # Tool input may be partial; we still try to return what we have but
        # warn — the frontend tolerates missing fields gracefully.
        log.warning(
            "Claude hit max_tokens=%d before finishing. Profile may be incomplete.",
            MAX_TOKENS,
        )

    profile = tool_block.input
    if not isinstance(profile, dict):
        log.error("Tool input is not a dict: %r", profile)
        raise HTTPException(status_code=502, detail="Risposta Claude non valida. Riprova.")

    return profile


def _enrich_with_urls(result: dict) -> dict:
    """Resolve each product's `categoria` to a verified URL from stores.py."""
    prodotti = result.get("prodotti") or {}
    if not isinstance(prodotti, dict):
        prodotti = {}

    for store_key in STORE_URLS.keys():
        items = prodotti.get(store_key) or []
        if not isinstance(items, list):
            items = []
        enriched = []
        for item in items:
            if not isinstance(item, dict):
                continue
            category = (item.get("categoria") or "").strip().lower()
            product_name = (item.get("nome") or "").strip()
            item["url"] = resolve_url(store_key, category, product_name)
            enriched.append(item)
        prodotti[store_key] = enriched

    result["prodotti"] = prodotti
    return result


# Serve the frontend from the same service. Mount LAST so /api/* takes priority.
_FRONTEND_DIR = (Path(__file__).resolve().parent.parent / "frontend").resolve()
if _FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(_FRONTEND_DIR), html=True), name="frontend")
