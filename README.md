# Il Libro dei Pensieri Muti — v2

Sito statico Astro (48 poesie, archivio, percorsi, galleria, pagina Instagram, commenti, PWA offline).

    npm install
    npm run dev       # anteprima locale
    npm run build     # genera dist/
    npm run data      # rigenera src/data/poems.json (da eseguire dopo ogni modifica ai file sotto)

## Diritto d'autore, visite e voti
- Ogni poesia riporta la nota «© Cuordivino. Tutti i diritti riservati», il richiamo all'art. 70 L. 633/1941 (citazione) e un link per **segnalare una copia non autorizzata** (apre un'e-mail gia' pronta). La pagina `/diritti/` spiega paternita', usi consentiti e vietati, come chiedere un'autorizzazione e i riferimenti normativi. Quando si copia un brano di una poesia, il testo copiato include l'attribuzione. `robots.txt` esprime la riserva dei diritti di estrazione di testo e dati. Il controllo di pubblicazione blocca l'uscita se una poesia non ha la nota.
- **Visite e voti** usano lo stesso servizio dei commenti (cartella `worker/`: ricordati di rieseguire `schema.sql`, ci sono tre tabelle nuove). Le visite sono anonime (niente cookie, niente IP salvato; "Do Not Track" rispettato). Ogni poesia ha un voto da 1 a 5 stelle; `/classifica/` mostra le piu' votate e le piu' lette; il report completo (visite per giorno e per poesia, voti, medie) sta in `/admin/` > Statistiche. Finche' il servizio non e' collegato, le stelle e la classifica restano spente con un messaggio.

## Il libro e il quaderno
- `src/data/libro.json`: titolo, sottotitolo, nota biografica, prefazione (Federico Barretta) e indice delle 4 sezioni, dal PDF del libro. La pagina `/libro/` li mostra.
- `scripts/integra_materiale.py quaderno.txt` importa le poesie del quaderno (**sempre tenendo il testo gia' presente** se un componimento e' doppio, anche solo per titolo) e scarta poesie di altri autori: elenco in `src/data/escluse.json`.
- Le poesie del quaderno stanno in **Il Quaderno**; quelle del profilo non incluse nel libro in **I Versi Nuovi**. I dati si ricostruiscono da soli a ogni pubblicazione.
- **Foto:** `python3 scripts/importa_foto.py cartella` importa foto nominate con il titolo della poesia (es. `Il lembo.jpg`, oppure `36 - Attimo sfuggente.jpg`); le dubbie (somiglianza < 0.9) non si importano e vengono elencate. Le foto hanno la precedenza su quelle generate. Gia' importate: 60.
- Immagini generate (solo come ripiego): `scripts/genera_immagini.py` crea immagini astratte in bianco e nero per le poesie senza immagine di Instagram (60 finora). Per metterne una vera, salva `public/images/gen/NUMERO.jpg` (1200x1500) e `NUMERO-800.webp` con lo stesso nome.
- Brani: `scripts/proponi_brani.py` propone un brano per ogni poesia che ne e' priva (`src/data/brani-proposti.json`); il brano scritto in `scripts/musica.csv` ha sempre la precedenza.
- Le poesie con linguaggio esplicito sono segnate "Versi espliciti" e non compaiono nella citazione casuale della home.

## La mappa
La pagina `/mappa/` mostra le poesie come una costellazione: ogni punto e' una poesia (colore = movimento), ogni cerchio dorato un tema. Si aggiorna da sola con i dati; c'e' anche la versione in elenco per chi usa la tastiera o uno screen reader.

## 0. Le poesie del profilo (99 in totale)
Il libro ha 48 poesie; sul profilo ce ne sono altre 51 tue, ora nel sito come **I Versi Nuovi**. `scripts/nuove_poesie.py <cartella-esportazione>` le importa dall'esportazione di Instagram e **separa da solo** i post che non sono tuoi (poesie firmate da altri autori, citazioni, doppioni): finiscono in `src/data/escluse.json` e non vengono pubblicati. Titoli, temi e citazioni dei versi nuovi sono proposte automatiche: correggile in `src/data/overrides.json`.

## 1. Instagram: collegamento continuo (consigliato)
Ogni giorno il sito controlla il profilo, importa i post nuovi (immagine, data e **indirizzo del post**), li abbina alle poesie con un punteggio di affidabilita' e si ripubblica da solo. Gli abbinamenti gia' fatti non cambiano; le correzioni a mano in `scripts/instagram-links.csv` (colonna `url` = indirizzo del post) hanno la precedenza. I post che non assomigliano a nessuna poesia compaiono in `/instagram/` come "Ultimi post" con il link a Instagram.

Una tantum:
1. Il profilo @refuso_di.verso deve essere **professionale** (Creator o Business: si cambia gratis da Impostazioni > Tipo di account).
2. Su https://developers.facebook.com crea un'app di tipo Business, aggiungi il prodotto **Instagram** > "API setup with Instagram login", aggiungi il tuo profilo come tester e genera il token con il permesso `instagram_business_basic`; scambialo con un token a lunga durata (60 giorni).
3. Nel repository GitHub: Settings > Secrets and variables > Actions > crea il segreto `IG_TOKEN` con quel token.
4. Facoltativo ma consigliato: crea un token personale GitHub (permesso sui segreti del repository) e salvalo come segreto `GH_PAT`: cosi' il token Instagram si rinnova da solo ogni giorno. Senza, va rigenerato ogni 60 giorni.
5. Actions > "Sincronizza Instagram" > Run workflow. La prima volta importa tutto lo storico (non serve l'esportazione).
Prova in locale: `IG_TOKEN=... python3 scripts/sync_instagram.py && npm run data`.

### In alternativa: esportazione una tantum
1. Instagram → Impostazioni → Centro gestione account → Le tue informazioni e autorizzazioni → Scarica le tue informazioni → **Post**, formato **JSON**, qualità massima.
2. Decomprimi lo zip e lancia:  `npm run instagram -- /percorso/della/cartella`
   Lo script abbina ogni post alla poesia con un punteggio di affidabilità (sicuro / da verificare / non abbinato), copia le immagini in `public/images/ig/` e scrive `src/data/instagram-map.json`.
3. Apri `scripts/instagram-links.csv`, incolla l'indirizzo di ogni post (l'esportazione non lo contiene) e correggi gli abbinamenti dubbi. Poi `npm run data`.
Ogni poesia mostra il suo post e il pulsante "Copia didascalia con link"; la pagina `/instagram/` porta da ogni immagine alla poesia; `/p/NUMERO/` è il link breve da usare in bio e didascalie.

## 2. I brani: partono da soli dentro la pagina
- Ogni poesia con un indirizzo YouTube **diretto** in `scripts/musica.csv` (colonna `youtube`) mostra un lettore nella pagina: il brano parte da solo, con dissolvenza, e ci sono i tasti **Pausa**, **Volume** e **Spegni la musica** (la scelta resta anche nelle altre poesie). Con "Leggi in silenzio" la musica si ferma.
- **Limite dei browser:** l'audio parte da solo solo dopo che il lettore ha toccato qualcosa nel sito (per esempio entrando da una poesia all'altra). Se qualcuno apre direttamente la pagina di una poesia, il brano parte senza audio e compare "Attiva l'audio".
- **Due versioni per ogni brano:** colonna `youtube` = video ufficiale, colonna `youtube_audio` = solo musica (traccia "Topic" o official audio, di solito senza pubblicita'). Se ci sono entrambe, nella poesia compaiono i tasti **Solo musica** e **Video** e la scelta resta anche nelle altre poesie; se ce n'e' una sola, il tasto non compare. Nel flusso "Trova i brani su YouTube" l'opzione **Rifai tutti i collegamenti** cerca da capo entrambe.
- I **link di ricerca** (Spotify, YouTube Music, Apple Music, SoundCloud) restano sempre sotto il lettore.
- `python3 scripts/proponi_brani.py` propone un brano per ogni poesia che ne e' priva, partendo dal testo (sono 50 proposte su 53 poesie, da ascoltare e confermare o cambiare in `musica.csv`; 3 poesie restano senza proposta).
- **Trovare gli indirizzi:** su GitHub, Actions > "Trova i brani su YouTube" > Run workflow. **Non serve nessuna chiave**: usa la ricerca pubblica di YouTube (se vuoi piu' affidabilita' puoi aggiungere la chiave gratuita YouTube Data API v3 come segreto `YT_API_KEY`). Sceglie solo video il cui titolo contiene brano e artista, scarta cover, dal vivo e tutorial, e controlla che il video sia incorporabile; i casi incerti restano vuoti. In alternativa si incollano a mano nella colonna `youtube` di `musica.csv` (la colonna `cerca_youtube` apre la ricerca gia' pronta).
- La musica non si puo' esportare da Instagram (non e' un file ed e' su licenza): il lettore usa i video ufficiali.

## 3. Commenti e note
- **Note private**: funzionano già, restano nel browser del lettore.
- **Commenti pubblici**: servono un piccolo servizio (cartella `worker/`, Cloudflare Worker + D1, gratuito per questi volumi) e un servizio di posta (Resend).
  1. `cd worker && npx wrangler d1 create pensieri-muti` → incolla l'id in `wrangler.toml`
  2. `npx wrangler d1 execute pensieri-muti --remote --file=schema.sql`
  3. segreti: `npx wrangler secret put ADMIN_TOKEN` (codice per la moderazione), `RESEND_API_KEY`, `OWNER_EMAIL`, `IP_SALT`
  4. `npx wrangler deploy` → copia l'indirizzo in `src/data/config.json` (`api`), `email` è già impostata su lamenteardente@gmail.com; usala anche come `OWNER_EMAIL` per ricevere le notifiche. Per le risposte automatiche via e-mail Resend richiede un mittente su un dominio tuo verificato (un indirizzo Gmail non può fare da mittente): in alternativa rispondi dal tuo Gmail con il pulsante "Scrivi un'e-mail" di `/admin/`
  5. moderazione e risposte: `/admin/` sul sito.
- Il lettore sceglie come essere ricontattato (e-mail, cellulare, Instagram, altro social); non è obbligatorio. Risposta via e-mail: inviata dal sistema. Cellulare e social: `/admin/` apre WhatsApp, SMS, chiamata o messaggio Instagram.
- Prima di attivarlo: completa e fai rivedere `/privacy/` (è una bozza).
- Senza `api` ma con `email` il modulo apre il programma di posta del lettore.

## Pubblicazione
Settings → Pages → Source: GitHub Actions; ogni push su `main` pubblica.

## Aggiornare il sito con GitHub Desktop
1. Sostituisci i file nella cartella del repository (tieni `.git`). 2. In GitHub Desktop scrivi un titolo e premi Commit to main. 3. Premi Push origin. 4. Controlla Actions: verde = online.
