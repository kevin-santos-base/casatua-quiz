# CasaTua — Quiz di stile con Claude AI

Web app del quiz "CasaTua" con backend FastAPI che protegge la chiave Anthropic
e frontend HTML servito dallo stesso servizio.

## Struttura

```
casatua-quiz/
├── backend/         FastAPI + chiamata a Claude
│   ├── main.py
│   ├── prompt.py    Le 12 domande + costruzione prompt
│   ├── stores.py    Mappa URL verificati per i 6 store
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   └── index.html   Quiz (servito automaticamente da FastAPI)
├── render.yaml      Configurazione deploy Render
└── README.md
```

## Avvio in locale

1. Installa Python 3.11+ e crea un virtual env nella cartella `backend/`:

   ```bash
   cd backend
   python3 -m venv .venv
   source .venv/bin/activate   # su Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Copia `.env.example` in `.env` e inserisci la tua chiave Anthropic:

   ```bash
   cp .env.example .env
   # apri .env e sostituisci ANTHROPIC_API_KEY con la tua chiave
   ```

3. Avvia il server:

   ```bash
   uvicorn main:app --reload --port 8000
   ```

4. Apri il browser su `http://localhost:8000`.

## Deploy su Render

Il file `render.yaml` configura tutto automaticamente.

1. Vai su [render.com](https://render.com) e accedi con il tuo account GitHub.
2. Clicca **New +** → **Blueprint**.
3. Seleziona il repository `casatua-quiz`.
4. Render rileva il file `render.yaml` e crea il servizio.
5. Nella schermata di configurazione, **imposta la variabile `ANTHROPIC_API_KEY`**
   con la tua chiave Anthropic (è marcata `sync: false` in `render.yaml`, quindi
   non viene mai salvata in git).
6. Avvia il deploy. Dopo 2-3 minuti l'app è online all'URL
   `https://casatua-quiz.onrender.com` (o nome simile, lo trovi nella dashboard).

> **Nota piano gratuito Render**: il servizio si "addormenta" dopo 15 minuti
> di inattività. La prima richiesta dopo lo sleep impiega ~30 secondi.
> Per evitarlo, passa al piano Starter ($7/mese) o usa un servizio di
> ping esterno (es. UptimeRobot, gratis).

## Come aggiornare la chiave Anthropic in futuro

Quando la chiave scade o vuoi ruotarla per sicurezza:

1. Vai su [console.anthropic.com](https://console.anthropic.com) → **API Keys**.
2. Clicca **Create Key**, dai un nome (es. "casatua-prod-2026") e copia la chiave.
   Apparirà solo una volta — copiala subito in un posto sicuro.
3. Vai sulla dashboard di Render → seleziona il servizio `casatua-quiz`.
4. **Environment** → trova `ANTHROPIC_API_KEY` → clicca **Edit** → incolla la
   nuova chiave → **Save**.
5. Render fa il redeploy automatico in ~30 secondi.
6. Torna su console.anthropic.com e **cancella la vecchia chiave** (Delete)
   così non è più utilizzabile.

## Come impostare un limite di spesa (consigliato)

Per evitare brutte sorprese in fattura:

1. Su [console.anthropic.com](https://console.anthropic.com) → **Settings** →
   **Limits**.
2. Imposta **Monthly spend limit** (es. 10 USD o 25 USD).
3. Imposta una **email di notifica** quando la spesa supera il 75%.

In più, il backend ha già un rate limit interno di 5 richieste al minuto per
IP, che evita gli abusi accidentali (loop, bot di scraping, ecc.).

## Come modificare le domande del quiz

Le 12 domande sono in due file e devono restare sincronizzate:

- `backend/prompt.py` (variabile `QUESTIONS`)
- `frontend/index.html` (variabile `QS` nel tag `<script>`)

## Come aggiungere/correggere link degli store

I link verso IKEA, Zara Home, Westwing, La Redoute, Rinascente e Merci Paris
sono in `backend/stores.py`. Modificali lì — Claude non sceglie più URL
direttamente, sceglie solo una "categoria" (es. `divano`, `lampada`) e il
backend la traduce nell'URL verificato corrispondente.

Per aggiungere una nuova categoria:

1. Aggiungila alla lista `CATEGORIES` in `stores.py`.
2. Aggiungi l'URL corrispondente per ogni store nel dizionario `STORE_URLS`.
3. (Facoltativo) Aggiungi un'emoji per la categoria in `frontend/index.html`,
   nella variabile `EMOJIS`.

## Note sui singoli store

| Store | Stato | Note |
|-------|-------|------|
| IKEA | OK | Categorie dirette, apertura nuova scheda funziona. |
| Zara Home | OK | Usa URL di ricerca (`/search?q=...`), stabile. |
| Westwing | OK | Categorie dirette. |
| La Redoute | OK | URL di categoria, alcuni marcati `# VERIFY` da controllare. |
| Rinascente | Parziale | Anti-bot aggressivo. Punta sempre alla categoria casa, l'utente naviga da lì. |
| Merci Paris | Parziale | Sito senza deep-linking stabile. Punta alle categorie principali. |

## Modifica del prompt inviato a Claude

Il prompt è in `backend/prompt.py`, funzione `build_prompt()`. Modificalo lì.
Dopo ogni modifica, fai commit e push: Render farà il redeploy automatico.

## Modello Claude

Default: `claude-haiku-4-5` — veloce, economico, buona qualità di scrittura.
Per migliorare ulteriormente la qualità (a costo ~3x): cambia
`ANTHROPIC_MODEL` su Render a `claude-sonnet-4-6`.

## Risoluzione problemi

**"Server non configurato"** → la variabile `ANTHROPIC_API_KEY` non è
impostata su Render. Controlla la sezione Environment.

**"Troppe richieste"** → hai fatto più di 5 quiz al minuto dallo stesso IP.
Aspetta un minuto.

**"La richiesta ha impiegato troppo tempo"** → Claude ha impiegato più di
60 secondi. Probabile fluctuation lato Anthropic. Riprova.

**Il quiz si carica ma resta in "Creo il tuo profilo..."** → controlla la
console del browser (F12). Se vedi errore 502/504 è un problema di Claude;
se vedi errore di rete, controlla che il servizio Render sia attivo.

**Schermata vuota cliccando su uno shop** → la piattaforma di hosting
(dove hai pubblicato il quiz) probabilmente apre il link dentro un iframe.
Il frontend tenta di aprire in nuova scheda + fallback a `window.top`;
se serve, contatta il supporto della piattaforma per consentire
`target="_blank"`.

## Contatto sviluppatore

Kevin Santos — sviluppo backend, integrazione Claude, deploy Render.
