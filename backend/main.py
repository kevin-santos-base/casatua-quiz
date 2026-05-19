"""
CasaTua quiz backend.

Single endpoint POST /api/quiz that:
- accepts the 12 quiz answers
- builds a prompt and calls Claude server-side
- validates the JSON response
- enriches each product with a verified URL from stores.STORE_URLS
- returns the result to the frontend
"""

import json
import logging
import os
import re
import time
from collections import defaultdict, deque
from pathlib import Path

import anthropic
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, conlist

from prompt import QUESTIONS, build_prompt
from stores import STORE_URLS, resolve_url

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("casatua")

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-haiku-4-5")
MAX_TOKENS = int(os.environ.get("MAX_TOKENS", "2000"))
CLAUDE_TIMEOUT_S = 45.0

if not ANTHROPIC_API_KEY:
    log.warning("ANTHROPIC_API_KEY is not set. /api/quiz will return 500 until configured.")

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None

app = FastAPI(title="CasaTua Quiz API")


# Simple in-memory rate limit: 5 requests per IP per minute.
# Good enough to stop accidental loops; for real abuse use a proper limiter.
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
        "key_configured": bool(ANTHROPIC_API_KEY),
    }


@app.post("/api/quiz")
def quiz(req: QuizRequest, request: Request):
    if client is None:
        raise HTTPException(status_code=500, detail="Server non configurato: ANTHROPIC_API_KEY mancante.")

    # Validate answers are in 0..3
    for i, a in enumerate(req.answers):
        if not (0 <= a <= 3):
            raise HTTPException(status_code=400, detail=f"Risposta non valida per Q{i + 1}.")

    ip = request.client.host if request.client else "unknown"
    if _rate_limited(ip):
        raise HTTPException(status_code=429, detail="Troppe richieste. Riprova fra un minuto.")

    prompt = build_prompt(req.answers)

    try:
        message = client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=MAX_TOKENS,
            timeout=CLAUDE_TIMEOUT_S,
            messages=[{"role": "user", "content": prompt}],
        )
    except anthropic.APITimeoutError:
        raise HTTPException(status_code=504, detail="Claude ha impiegato troppo tempo. Riprova.")
    except anthropic.RateLimitError:
        raise HTTPException(status_code=429, detail="Limite di richieste Anthropic raggiunto. Riprova fra poco.")
    except anthropic.APIStatusError as e:
        log.exception("Anthropic API error")
        raise HTTPException(status_code=502, detail=f"Errore Anthropic ({e.status_code}). Riprova.")
    except Exception:
        log.exception("Unexpected error calling Anthropic")
        raise HTTPException(status_code=500, detail="Errore interno. Riprova.")

    if not message.content or not getattr(message.content[0], "text", None):
        raise HTTPException(status_code=502, detail="Risposta Claude vuota.")

    raw = message.content[0].text
    result = _parse_json(raw)
    result = _enrich_with_urls(result)
    return JSONResponse(result)


def _parse_json(text: str) -> dict:
    """Extract the JSON object from Claude's response, tolerating stray text."""
    text = text.strip()
    # Strip markdown fences if Claude returns them despite instructions.
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise HTTPException(status_code=502, detail="Risposta Claude non in formato JSON.")
    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError as e:
        log.error("JSON parse failed: %s\n--- raw ---\n%s", e, text[:500])
        raise HTTPException(status_code=502, detail="Risposta Claude non valida (JSON).")


def _enrich_with_urls(result: dict) -> dict:
    """Replace any url field from Claude with a verified URL from stores.py."""
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
            item["url"] = resolve_url(store_key, category)
            enriched.append(item)
        prodotti[store_key] = enriched

    result["prodotti"] = prodotti
    return result


# Serve the frontend from the same service. Mount LAST so /api/* takes priority.
_FRONTEND_DIR = (Path(__file__).resolve().parent.parent / "frontend").resolve()
if _FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(_FRONTEND_DIR), html=True), name="frontend")
