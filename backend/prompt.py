"""
Prompt and tool schema for the Claude call.

We use Anthropic tool use (structured output): instead of asking Claude to
return free-form JSON text, we declare a tool with a strict JSON schema and
force Claude to call it. Claude fills the schema, and the SDK returns it as
a parsed dict — no string parsing, no truncation-related JSONDecodeError,
no markdown fence stripping.
"""

from stores import CATEGORIES, STORE_URLS

LETTERS = ["A", "B", "C", "D"]

# The 12 quiz questions, kept in sync with frontend/index.html (`QS` array).
QUESTIONS = [
    {"t": "Come descriveresti il tuo ritmo quotidiano?",
     "o": ["Strutturato e prevedibile - mi piace sapere cosa mi aspetta",
           "Flessibile e spontaneo - ogni giorno e diverso",
           "Intenso e produttivo - lavoro molto, mi fermo poco",
           "Lento e contemplativo - ho bisogno di spazio mentale"]},
    {"t": "Quando sei a casa, come passi il tempo libero?",
     "o": ["Leggo, ascolto musica, mi rilasso in silenzio",
           "Cucino, ricevo amici, voglio che la casa sia viva",
           "Lavoro, creo, ho sempre qualcosa da fare",
           "Guardo serie, mi sdraio, cerco comfort totale"]},
    {"t": "Quale parola ti rappresenta di piu?",
     "o": ["Ordine", "Calore", "Creativita", "Liberta"]},
    {"t": "Come reagisci al disordine visivo?",
     "o": ["Mi disturba molto - ho bisogno di tutto al posto suo",
           "Mi disturba un po ma riesco a ignorarlo",
           "Non mi influenza - vedo la bellezza nel caos",
           "Mi piace un certo disordine, sembra vissuto"]},
    {"t": "Quale paesaggio ti fa sentire piu te stesso?",
     "o": ["Una foresta nordica - silenziosa, fredda, pulita",
           "Una casa di campagna - calda, profumata, imperfetta",
           "Un loft urbano - dinamico, crudo, contemporaneo",
           "Una villa mediterranea - luce, colori, aria aperta"]},
    {"t": "Qual e il tuo rapporto con i ricordi e gli oggetti personali?",
     "o": ["Conservo poco - preferisco essenziale e pulito",
           "Amo esporre oggetti che raccontano la mia storia",
           "Mix: tengo l essenziale ma con significato",
           "Colleziono, accumulo, ogni pezzo ha un valore"]},
    {"t": "Come ti senti in uno spazio molto minimalista?",
     "o": ["Sereno e libero - e esattamente quello che voglio",
           "Un po freddo - mi manca calore umano",
           "Ispirato - mi aiuta a pensare meglio",
           "Vuoto e scomodo - ho bisogno di piu"]},
    {"t": "Quale materiale senti piu vicino alla tua personalita?",
     "o": ["Legno naturale - autentico, caldo, imperfetto",
           "Cemento e acciaio - deciso, contemporaneo, crudo",
           "Marmo e ottone - raffinato, senza tempo, elegante",
           "Tessuti morbidi - avvolgente, accogliente, sensoriale"]},
    {"t": "Come preferisci la luce in casa?",
     "o": ["Molta luce naturale, finestre grandi, aria aperta",
           "Luce calda e diffusa, lampade e candele",
           "Contrasti forti - zone illuminate e zone d ombra",
           "Luce regolabile - voglio sceglierla in base all umore"]},
    {"t": "Come ti comporti con le tendenze?",
     "o": ["Le ignoro - voglio qualcosa di intramontabile",
           "Mi ispirano ma le reinterpreto a modo mio",
           "Le seguo volentieri - mi piace stare al passo",
           "Le anticipo - mi piace essere avanti"]},
    {"t": "Cosa deve trasmettere la tua casa a chi entra?",
     "o": ["Calma e ordine - qui si respira",
           "Calore e accoglienza - qui ci si sente a casa",
           "Personalita forte - qui vive qualcuno di unico",
           "Eleganza discreta - qui c e gusto"]},
    {"t": "Quale frase senti piu tua?",
     "o": ["Less is more - Mies van der Rohe",
           "La casa e dove il cuore e - proverbio",
           "Ogni oggetto racconta una storia - collezionista",
           "Il lusso e la semplicita perfetta - Coco Chanel"]},
]

# Store keys must match those in stores.STORE_URLS.
_STORE_KEYS = list(STORE_URLS.keys())

_PRODUCT_SCHEMA = {
    "type": "object",
    "properties": {
        "nome": {"type": "string", "description": "Nome del prodotto in italiano"},
        "descrizione": {"type": "string", "description": "Breve descrizione del prodotto in italiano"},
        "prezzo": {"type": "string", "description": "Prezzo come stringa, es. '49 EUR' o '129,99 EUR'"},
        "categoria": {
            "type": "string",
            "enum": CATEGORIES,
            "description": "Categoria fissa scelta dall'elenco — il backend la convertira in URL verificato",
        },
    },
    "required": ["nome", "descrizione", "prezzo", "categoria"],
}

_COLOR_SCHEMA = {
    "type": "object",
    "properties": {
        "nome": {"type": "string", "description": "Nome del colore in italiano"},
        "hex": {"type": "string", "description": "Codice esadecimale, es. '#F5F0E8'"},
        "ruolo": {"type": "string", "enum": ["primary", "secondary", "accent", "neutral"]},
    },
    "required": ["nome", "hex", "ruolo"],
}

PROFILE_TOOL = {
    "name": "submit_style_profile",
    "description": (
        "Submit the completed personalised home decor style profile based on "
        "the user's quiz answers. All text values MUST be in Italian. The "
        "profile is shown to the user as the final result."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "nome_profilo": {"type": "string", "description": "Nome evocativo del profilo, max 4 parole"},
            "sottotitolo": {"type": "string", "description": "Sottotitolo poetico, 1 riga"},
            "descrizione": {"type": "string", "description": "2-3 frasi sulla personalita e lo stile"},
            "stile_principale": {"type": "string", "description": "Nome dello stile principale"},
            "descrizione_stile": {"type": "string", "description": "2 frasi su questo stile"},
            "palette_colori": {
                "type": "array",
                "items": _COLOR_SCHEMA,
                "minItems": 4,
                "maxItems": 4,
                "description": "Esattamente 4 colori con ruoli primary, secondary, accent, neutral",
            },
            "materiali": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 3,
                "maxItems": 5,
            },
            "elementi_chiave": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 3,
                "maxItems": 6,
            },
            "da_evitare": {"type": "string", "description": "Cosa evitare, 1-2 frasi"},
            "consiglio_personale": {"type": "string", "description": "Consiglio personalizzato, 2-3 frasi"},
            "prodotti": {
                "type": "object",
                "properties": {
                    store: {
                        "type": "array",
                        "items": _PRODUCT_SCHEMA,
                        "minItems": 3,
                        "maxItems": 3,
                        "description": f"Esattamente 3 prodotti per {store}",
                    }
                    for store in _STORE_KEYS
                },
                "required": _STORE_KEYS,
            },
        },
        "required": [
            "nome_profilo",
            "sottotitolo",
            "descrizione",
            "stile_principale",
            "descrizione_stile",
            "palette_colori",
            "materiali",
            "elementi_chiave",
            "da_evitare",
            "consiglio_personale",
            "prodotti",
        ],
    },
}


def build_user_message(answers: list[int]) -> str:
    """Build the user-facing prompt that goes alongside the tool call."""
    summary_lines = []
    for i, q in enumerate(QUESTIONS):
        idx = answers[i]
        summary_lines.append(f"Q{i + 1}: {q['t']} -> {LETTERS[idx]}) {q['o'][idx]}")
    summary = "\n".join(summary_lines)

    return f"""Sei un interior designer italiano esperto. Analizza queste 12 risposte di un quiz e proponi un profilo di arredamento personalizzato chiamando lo strumento submit_style_profile.

RISPOSTE QUIZ:
{summary}

LINEE GUIDA:
- Tutti i testi devono essere in italiano.
- Per ogni store suggerisci esattamente 3 prodotti, scegliendo "categoria" da quelle ammesse (es. divano, lampada, cuscino...). Il backend tradurra ogni categoria nell'URL verificato dello store, quindi NON inventare URL.
- La palette deve avere 4 colori con i ruoli primary, secondary, accent, neutral.
- I prodotti suggeriti devono essere coerenti tra loro e con lo stile del profilo.
- Sii specifico e autentico nella scelta dello stile."""
