# IL LIBRO DEI PENSIERI MUTI

> Opera poetica interattiva di [@refuso_di.verso](https://www.instagram.com/refuso_di.verso/) (Cuordivino)

48 poesie in chiaroscuro, ciascuna con la sua fotografia in bianco e nero e il suo stato d'animo, da sfogliare come un libro aperto.

**Sito:** https://cuordivino.github.io/libro-dei-pensieri-muti/

---

## Cosa c'è nel sito

- **Libro aperto** a doppia pagina: a sinistra fotografia, traccia e senso dello stato d'animo; a destra i versi. Navigazione con frecce a schermo, tastiera (`←` `→`), cursore o swipe.
- **Galleria & Musica**, **Stati d'animo** (4 movimenti: *L'Ombra e il Pozzo*, *L'Ardore e la Carne*, *La Maschera e il Fango*, *La Quiete e il Ritrovo*) e **Indice** con ricerca.
- **Card per Instagram** (1080×1350) in tre stili, generata direttamente nel browser.
- **Atmosfera sonora** generata dal browser (pioggia, focolare, arpeggi), senza file audio.
- **Link diretti** a ogni poesia: `…/#poesia-12`, e alle sezioni `#galleria`, `#stati`, `#indice`, `#copertina`.
- **Funziona offline** dopo la prima visita e si può installare come app (PWA).

## Struttura

| File | Ruolo |
| --- | --- |
| `index.html`, `styles.css`, `app.js` | Pagina, stile e logica |
| `data.js` / `poems.json` | Le 48 poesie e i metadati (stessa fonte, due formati) |
| `images/` | Le 48 fotografie |
| `LIBRO_DEI_PENSIERI_MUTI.md` | Manoscritto completo in Markdown |
| `sw.js`, `manifest.webmanifest` | Offline e installazione |
| `404.html`, `og-image.jpg`, icone | Pagina di errore e anteprime social |
| `tools/` | Script Python per rigenerare dati, immagini e manoscritto |
| `.github/workflows/pages.yml` | Pubblicazione automatica su GitHub Pages |

## Pubblicare su GitHub Pages

1. Crea su github.com un repository **pubblico** chiamato `libro-dei-pensieri-muti` (vuoto: senza README né licenza).
2. Dalla cartella del progetto, in PowerShell: `.\pubblica.ps1`
   (oppure a mano: `git init -b main`, `git add .`, `git commit -m "Il Libro dei Pensieri Muti"`, `git remote add origin https://github.com/cuordivino/libro-dei-pensieri-muti.git`, `git push -u origin main`).
3. Nel repository: **Settings → Pages → Build and deployment → Source: GitHub Actions**.
4. Al primo push parte il workflow; dopo circa un minuto il sito è online all'indirizzo qui sopra. Ogni push successivo su `main` lo aggiorna.

Se cambi nome del repository o dell'account, aggiorna l'indirizzo in `index.html` (tag `canonical` e `og:`) e in questo file.

## Modificare i contenuti

- **Testi e stati d'animo:** modifica `tools/build_data.py` e lancia `python tools/build_data.py` (rigenera `data.js` e `poems.json`), poi `python tools/generate_md.py` per il manoscritto.
- **Foto:** sostituisci i file in `images/` (800×1000, `poesia_N.jpg`) oppure rigenerale con `python tools/generate_photos.py`.
- **Dopo ogni modifica** cambia `VERSION` in `sw.js` (ad es. `v2`) perché chi ha già visitato il sito riceva i contenuti nuovi.
- **Strumenti di modifica nel browser:** aggiungere poesie, sostituire foto o audio dal sito funziona solo sul tuo browser (i dati restano nel `localStorage`, non sul sito pubblico). Si attivano aprendo il sito con `?edit=1` e si disattivano con `?edit=0`; i visitatori non li vedono.

## Prova in locale

```bash
python -m http.server 8000
# poi apri http://localhost:8000
```

Il service worker e la copia negli appunti richiedono `http://localhost` o `https`; aprendo `index.html` con doppio clic il libro funziona, ma senza offline.

## Licenza

Testi e fotografie © Cuordivino, tutti i diritti riservati. Il codice è con licenza MIT. Dettagli in [`LICENSE`](LICENSE).
