"""
Curated URL map for the six partner stores.

Claude returns a category slug per product (e.g. "divano", "lampada"). The
backend resolves that slug to a verified URL using this map, so the AI cannot
hallucinate broken links. If a slug is missing, we fall back to the store
homepage.

Each URL should be verified manually before deploying. Marked with `# VERIFY`
where a URL is best-effort and should be double-checked in the browser.
"""

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
        "_home": "https://www.zarahome.com/it/",
        "divano": "https://www.zarahome.com/it/search?q=divano",
        "poltrona": "https://www.zarahome.com/it/search?q=poltrona",
        "tavolino": "https://www.zarahome.com/it/search?q=tavolino",
        "lampada": "https://www.zarahome.com/it/search?q=lampada",
        "tappeto": "https://www.zarahome.com/it/search?q=tappeto",
        "cuscino": "https://www.zarahome.com/it/search?q=cuscino",
        "vaso": "https://www.zarahome.com/it/search?q=vaso",
        "candela": "https://www.zarahome.com/it/search?q=candela",
        "specchio": "https://www.zarahome.com/it/search?q=specchio",
        "tenda": "https://www.zarahome.com/it/search?q=tenda",
        "decorazione": "https://www.zarahome.com/it/search?q=decorazione",
        "tessuto": "https://www.zarahome.com/it/search?q=plaid",
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


def resolve_url(store: str, category: str) -> str:
    """Resolve a (store, category) pair to a verified URL.

    Falls back to the store homepage when category is unknown.
    """
    store_map = STORE_URLS.get(store)
    if not store_map:
        return ""
    return store_map.get(category) or store_map["_home"]
