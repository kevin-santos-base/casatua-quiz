"""Builder for the Claude prompt that turns quiz answers into a style profile."""

from stores import CATEGORIES

# The 12 quiz questions, kept in sync with frontend/index.html (`QS` array).
QUESTIONS = [
    {
        "t": "Come descriveresti il tuo ritmo quotidiano?",
        "o": [
            "Strutturato e prevedibile - mi piace sapere cosa mi aspetta",
            "Flessibile e spontaneo - ogni giorno e diverso",
            "Intenso e produttivo - lavoro molto, mi fermo poco",
            "Lento e contemplativo - ho bisogno di spazio mentale",
        ],
    },
    {
        "t": "Quando sei a casa, come passi il tempo libero?",
        "o": [
            "Leggo, ascolto musica, mi rilasso in silenzio",
            "Cucino, ricevo amici, voglio che la casa sia viva",
            "Lavoro, creo, ho sempre qualcosa da fare",
            "Guardo serie, mi sdraio, cerco comfort totale",
        ],
    },
    {
        "t": "Quale parola ti rappresenta di piu?",
        "o": ["Ordine", "Calore", "Creativita", "Liberta"],
    },
    {
        "t": "Come reagisci al disordine visivo?",
        "o": [
            "Mi disturba molto - ho bisogno di tutto al posto suo",
            "Mi disturba un po ma riesco a ignorarlo",
            "Non mi influenza - vedo la bellezza nel caos",
            "Mi piace un certo disordine, sembra vissuto",
        ],
    },
    {
        "t": "Quale paesaggio ti fa sentire piu te stesso?",
        "o": [
            "Una foresta nordica - silenziosa, fredda, pulita",
            "Una casa di campagna - calda, profumata, imperfetta",
            "Un loft urbano - dinamico, crudo, contemporaneo",
            "Una villa mediterranea - luce, colori, aria aperta",
        ],
    },
    {
        "t": "Qual e il tuo rapporto con i ricordi e gli oggetti personali?",
        "o": [
            "Conservo poco - preferisco essenziale e pulito",
            "Amo esporre oggetti che raccontano la mia storia",
            "Mix: tengo l essenziale ma con significato",
            "Colleziono, accumulo, ogni pezzo ha un valore",
        ],
    },
    {
        "t": "Come ti senti in uno spazio molto minimalista?",
        "o": [
            "Sereno e libero - e esattamente quello che voglio",
            "Un po freddo - mi manca calore umano",
            "Ispirato - mi aiuta a pensare meglio",
            "Vuoto e scomodo - ho bisogno di piu",
        ],
    },
    {
        "t": "Quale materiale senti piu vicino alla tua personalita?",
        "o": [
            "Legno naturale - autentico, caldo, imperfetto",
            "Cemento e acciaio - deciso, contemporaneo, crudo",
            "Marmo e ottone - raffinato, senza tempo, elegante",
            "Tessuti morbidi - avvolgente, accogliente, sensoriale",
        ],
    },
    {
        "t": "Come preferisci la luce in casa?",
        "o": [
            "Molta luce naturale, finestre grandi, aria aperta",
            "Luce calda e diffusa, lampade e candele",
            "Contrasti forti - zone illuminate e zone d ombra",
            "Luce regolabile - voglio sceglierla in base all umore",
        ],
    },
    {
        "t": "Come ti comporti con le tendenze?",
        "o": [
            "Le ignoro - voglio qualcosa di intramontabile",
            "Mi ispirano ma le reinterpreto a modo mio",
            "Le seguo volentieri - mi piace stare al passo",
            "Le anticipo - mi piace essere avanti",
        ],
    },
    {
        "t": "Cosa deve trasmettere la tua casa a chi entra?",
        "o": [
            "Calma e ordine - qui si respira",
            "Calore e accoglienza - qui ci si sente a casa",
            "Personalita forte - qui vive qualcuno di unico",
            "Eleganza discreta - qui c e gusto",
        ],
    },
    {
        "t": "Quale frase senti piu tua?",
        "o": [
            "Less is more - Mies van der Rohe",
            "La casa e dove il cuore e - proverbio",
            "Ogni oggetto racconta una storia - collezionista",
            "Il lusso e la semplicita perfetta - Coco Chanel",
        ],
    },
]

LETTERS = ["A", "B", "C", "D"]


def build_prompt(answers: list[int]) -> str:
    """Return the user-message prompt for Claude."""
    summary_lines = []
    for i, q in enumerate(QUESTIONS):
        idx = answers[i]
        summary_lines.append(f"Q{i + 1}: {q['t']} -> {LETTERS[idx]}) {q['o'][idx]}")
    summary = "\n".join(summary_lines)

    categories_csv = ", ".join(CATEGORIES)

    return f"""You are an expert Italian interior designer. Based on these 12 quiz answers, create a personalised home decor profile in Italian.

QUIZ ANSWERS:
{summary}

OUTPUT RULES:
- Respond ONLY with valid JSON. No markdown fences, no backticks, no commentary.
- All text fields MUST be in Italian.
- For each product, "categoria" MUST be exactly one of: {categories_csv}.
- Do NOT invent URLs. The backend will resolve URLs from the category.
- Suggest 3 products per store, choosing categories that fit the style profile.

OUTPUT JSON STRUCTURE:
{{
  "nome_profilo": "Nome evocativo del profilo, max 4 parole",
  "sottotitolo": "Sottotitolo poetico, 1 riga",
  "descrizione": "2-3 frasi sulla personalita e lo stile",
  "stile_principale": "Nome dello stile principale (es. Minimalismo Scandinavo)",
  "descrizione_stile": "2 frasi su questo stile",
  "palette_colori": [
    {{"nome": "Nome colore", "hex": "#RRGGBB", "ruolo": "primary"}},
    {{"nome": "Nome colore", "hex": "#RRGGBB", "ruolo": "secondary"}},
    {{"nome": "Nome colore", "hex": "#RRGGBB", "ruolo": "accent"}},
    {{"nome": "Nome colore", "hex": "#RRGGBB", "ruolo": "neutral"}}
  ],
  "materiali": ["materiale 1", "materiale 2", "materiale 3"],
  "elementi_chiave": ["elemento 1", "elemento 2", "elemento 3", "elemento 4"],
  "da_evitare": "Cosa evitare, 1-2 frasi",
  "consiglio_personale": "Consiglio personalizzato, 2-3 frasi",
  "prodotti": {{
    "ikea":       [{{"nome": "Nome prodotto", "descrizione": "Breve descrizione", "prezzo": "XX EUR", "categoria": "divano"}}],
    "zara":       [{{"nome": "Nome prodotto", "descrizione": "Breve descrizione", "prezzo": "XX EUR", "categoria": "cuscino"}}],
    "westwing":   [{{"nome": "Nome prodotto", "descrizione": "Breve descrizione", "prezzo": "XX EUR", "categoria": "lampada"}}],
    "redoute":    [{{"nome": "Nome prodotto", "descrizione": "Breve descrizione", "prezzo": "XX EUR", "categoria": "tappeto"}}],
    "rinascente": [{{"nome": "Nome prodotto", "descrizione": "Breve descrizione", "prezzo": "XX EUR", "categoria": "vaso"}}],
    "merci":      [{{"nome": "Nome prodotto", "descrizione": "Breve descrizione", "prezzo": "XX EUR", "categoria": "decorazione"}}]
  }}
}}

Each store array MUST contain exactly 3 products."""
