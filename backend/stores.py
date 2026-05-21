"""
Curated URL map for the six partner stores.

Claude returns a category slug per product (e.g. "divano", "lampada") plus
a human-readable product name. The backend resolves the category to a base
URL from STORE_URLS, then optionally refines the URL using keywords from the
product name so the user lands on a tighter list of items that match the
AI's specific suggestion (Option C in the phase-2 design discussion).

For stores using a search endpoint (Zara Home today, others later), the
refinement appends up to 2 descriptors from the product name to the existing
search term. For stores using category-path URLs, the URL is returned
unmodified.

Each URL should be verified manually before deploying. Marked with `# VERIFY`
where a URL is best-effort and should be double-checked in the browser.
"""

from urllib.parse import urlencode, urlparse, parse_qs, quote_plus

# Canonical category slugs used in the prompt sent to Claude.
# Keep this list short and broad — the AI works better with fewer options.
CATEGORIES = [
    "divano",
    "poltrona",
    "tavolino",
    "lampada",
    "tappeto",
    "cuscino",
    "vaso",
    "candela",
    "specchio",
    "tenda",
    "decorazione",
    "tessuto",
]

STORE_URLS = {
    "ikea": {
        "_home": "https://www.ikea.com/it/it/",
        "divano": "https://www.ikea.com/it/it/cat/divani-fu003/",
        "poltrona": "https://www.ikea.com/it/it/cat/poltrone-fu002/",
        "tavolino": "https://www.ikea.com/it/it/cat/tavolini-da-salotto-20649/",
        "lampada": "https://www.ikea.com/it/it/cat/illuminazione-lighting/",
        "tappeto": "https://www.ikea.com/it/it/cat/tappeti-rugs-fu002/",  # VERIFY
        "cuscino": "https://www.ikea.com/it/it/cat/cuscini-decorativi-20734/",
        "vaso": "https://www.ikea.com/it/it/cat/vasi-vases-20674/",  # VERIFY
        "candela": "https://www.ikea.com/it/it/cat/candele-candele-profumate-20675/",  # VERIFY
        "specchio": "https://www.ikea.com/it/it/cat/specchi-mirrors-fu004/",  # VERIFY
        "tenda": "https://www.ikea.com/it/it/cat/tende-curtains-fu004/",  # VERIFY
        "decorazione": "https://www.ikea.com/it/it/cat/decorazione-home-decoration/",
        "tessuto": "https://www.ikea.com/it/it/cat/tessili-textiles/",
    },
    "zara": {
        # Zara Home Italy search endpoint is /it/search.html with param name
        # `term`. Confirmed working against the live site (e.g. cuscino).
        # Zara Home specialises in textiles, scents, decor and lighting
        # rather than large furniture, so categories like sofa/armchair/
        # coffee-table are mapped to the closest stocked alternative
        # (covers, throws, table linens) instead of an empty result page.
        "_home": "https://www.zarahome.com/it/",
        "divano": "https://www.zarahome.com/it/search.html?term=copridivano",
        "poltrona": "https://www.zarahome.com/it/search.html?term=poltrona",
        "tavolino": "https://www.zarahome.com/it/search.html?term=tovaglia+lino",
        "lampada": "https://www.zarahome.com/it/search.html?term=lampada",
        "tappeto": "https://www.zarahome.com/it/search.html?term=tappeto",
        "cuscino": "https://www.zarahome.com/it/search.html?term=cuscino",
        "vaso": "https://www.zarahome.com/it/search.html?term=vaso",
        "candela": "https://www.zarahome.com/it/search.html?term=candela",
        "specchio": "https://www.zarahome.com/it/search.html?term=specchio",
        "tenda": "https://www.zarahome.com/it/search.html?term=tenda",
        "decorazione": "https://www.zarahome.com/it/search.html?term=decorazione",
        "tessuto": "https://www.zarahome.com/it/search.html?term=coperta",
    },
    "westwing": {
        "_home": "https://www.westwing.it/",
        "divano": "https://www.westwing.it/divani/",
        "poltrona": "https://www.westwing.it/poltrone/",
        "tavolino": "https://www.westwing.it/tavolini/",
        "lampada": "https://www.westwing.it/illuminazione/",
        "tappeto": "https://www.westwing.it/tappeti/",
        "cuscino": "https://www.westwing.it/cuscini/",
        "vaso": "https://www.westwing.it/vasi/",
        "candela": "https://www.westwing.it/candele/",
        "specchio": "https://www.westwing.it/specchi/",
        "tenda": "https://www.westwing.it/tende/",
        "decorazione": "https://www.westwing.it/accessori/",
        "tessuto": "https://www.westwing.it/tessuti-casa/",
    },
    "redoute": {
        "_home": "https://www.laredoute.it/pplp/cat-deco-maison.aspx",
        "divano": "https://www.laredoute.it/ppdp/cat-divani.aspx",  # VERIFY
        "poltrona": "https://www.laredoute.it/ppdp/cat-poltrone.aspx",  # VERIFY
        "tavolino": "https://www.laredoute.it/ppdp/cat-tavolini.aspx",  # VERIFY
        "lampada": "https://www.laredoute.it/ppdp/cat-illuminazione.aspx",  # VERIFY
        "tappeto": "https://www.laredoute.it/ppdp/cat-tappeti.aspx",  # VERIFY
        "cuscino": "https://www.laredoute.it/ppdp/cat-cuscini.aspx",  # VERIFY
        "vaso": "https://www.laredoute.it/ppdp/cat-decorazione.aspx",  # VERIFY
        "candela": "https://www.laredoute.it/ppdp/cat-decorazione.aspx",  # VERIFY
        "specchio": "https://www.laredoute.it/ppdp/cat-specchi.aspx",  # VERIFY
        "tenda": "https://www.laredoute.it/ppdp/cat-tende.aspx",  # VERIFY
        "decorazione": "https://www.laredoute.it/pplp/cat-deco-maison.aspx",
        "tessuto": "https://www.laredoute.it/ppdp/cat-tessuti.aspx",  # VERIFY
    },
    "rinascente": {
        # NOTE: Rinascente has aggressive geo / bot protection. Several pages
        # may show an error page when opened from inside an embedding iframe.
        # We point to the main category to maximise the chance of working.
        "_home": "https://www.rinascente.it/rinascente/it/categoria/casa-design",
        "divano": "https://www.rinascente.it/rinascente/it/categoria/casa-design",
        "poltrona": "https://www.rinascente.it/rinascente/it/categoria/casa-design",
        "tavolino": "https://www.rinascente.it/rinascente/it/categoria/casa-design",
        "lampada": "https://www.rinascente.it/rinascente/it/categoria/casa-design/illuminazione",  # VERIFY
        "tappeto": "https://www.rinascente.it/rinascente/it/categoria/casa-design",
        "cuscino": "https://www.rinascente.it/rinascente/it/categoria/casa-design",
        "vaso": "https://www.rinascente.it/rinascente/it/categoria/casa-design/vasi",  # VERIFY
        "candela": "https://www.rinascente.it/rinascente/it/categoria/casa-design/profumeria-casa",  # VERIFY
        "specchio": "https://www.rinascente.it/rinascente/it/categoria/casa-design",
        "tenda": "https://www.rinascente.it/rinascente/it/categoria/casa-design",
        "decorazione": "https://www.rinascente.it/rinascente/it/categoria/casa-design",
        "tessuto": "https://www.rinascente.it/rinascente/it/categoria/casa-design",
    },
    "merci": {
        # NOTE: Merci Paris does not offer category deep-linking in a stable way.
        # All categories point to the e-commerce homepage section that is
        # known to load reliably.
        "_home": "https://www.merci-merci.com/en/",
        "divano": "https://www.merci-merci.com/en/categorie/furniture.html",  # VERIFY
        "poltrona": "https://www.merci-merci.com/en/categorie/furniture.html",  # VERIFY
        "tavolino": "https://www.merci-merci.com/en/categorie/furniture.html",  # VERIFY
        "lampada": "https://www.merci-merci.com/en/categorie/lighting.html",  # VERIFY
        "tappeto": "https://www.merci-merci.com/en/categorie/textile.html",  # VERIFY
        "cuscino": "https://www.merci-merci.com/en/categorie/textile.html",  # VERIFY
        "vaso": "https://www.merci-merci.com/en/categorie/tableware.html",  # VERIFY
        "candela": "https://www.merci-merci.com/en/categorie/perfume.html",  # VERIFY
        "specchio": "https://www.merci-merci.com/en/categorie/furniture.html",  # VERIFY
        "tenda": "https://www.merci-merci.com/en/categorie/textile.html",  # VERIFY
        "decorazione": "https://www.merci-merci.com/en/categorie/objet.html",  # VERIFY
        "tessuto": "https://www.merci-merci.com/en/categorie/textile.html",  # VERIFY
    },
}


_ITALIAN_STOP_WORDS = frozenset({
    # articles
    "il", "lo", "la", "i", "gli", "le", "un", "uno", "una",
    # simple prepositions
    "di", "a", "da", "in", "con", "su", "per", "tra", "fra", "ad",
    # combined prepositions
    "del", "della", "dei", "delle", "dello", "dell",
    "al", "alla", "ai", "alle", "allo",
    "dal", "dalla", "dai", "dalle", "dallo",
    "nel", "nella", "nei", "nelle", "nello",
    "sul", "sulla", "sui", "sulle", "sullo",
    # conjunctions and other tiny fillers
    "e", "ed", "o", "od", "ma", "se", "che", "non", "anche",
})

# Query-parameter names commonly used by store search endpoints. We look for
# any of these when deciding whether a URL is "search-shaped" and can be
# refined with extra keywords.
_SEARCH_PARAMS = ("term", "q", "query", "searchTerm")


def _refine_search_url(base_url: str, product_name: str, max_extra: int = 2) -> str:
    """If base_url is a search URL, append meaningful keywords from product_name.

    Returns base_url unchanged when product_name is empty, when the URL has no
    recognised search parameter, or when no new keywords can be extracted.
    """
    if not product_name:
        return base_url
    try:
        parsed = urlparse(base_url)
    except Exception:
        return base_url
    qs = parse_qs(parsed.query)

    search_key = next((k for k in _SEARCH_PARAMS if k in qs), None)
    if not search_key:
        return base_url
    current_term = (qs[search_key][0] if qs[search_key] else "").strip()
    if not current_term:
        return base_url

    existing = {w.lower() for w in current_term.split()}
    extras: list[str] = []
    for raw in product_name.split():
        word = raw.strip(",.!?-:;()—–‘’“”").lower()
        if not word or word in _ITALIAN_STOP_WORDS or word in existing:
            continue
        existing.add(word)
        extras.append(word)
        if len(extras) >= max_extra:
            break

    if not extras:
        return base_url

    new_term = " ".join([current_term] + extras)
    new_query = urlencode([(search_key, new_term)], quote_via=quote_plus)
    return parsed._replace(query=new_query).geturl()


def resolve_url(store: str, category: str, product_name: str = "") -> str:
    """Resolve a (store, category) pair to a URL, optionally refined with the
    product name to land on a more specific search result.

    Falls back to the store homepage when category is unknown.
    """
    store_map = STORE_URLS.get(store)
    if not store_map:
        return ""
    base = store_map.get(category) or store_map["_home"]
    return _refine_search_url(base, product_name)
