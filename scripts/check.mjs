// Controllo prima della pubblicazione: `npm run check` (costruisce il sito e lo verifica).
// Errori = bloccano la pubblicazione. Avvisi = cose da completare, non bloccano.
import fs from 'node:fs'; import path from 'node:path';
const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const DIST = path.join(ROOT, 'dist'), BASE = '/libro-dei-pensieri-muti';
const errors = [], warns = [];
const err = (m) => errors.push(m), warn = (m) => warns.push(m);
const read = (f) => fs.readFileSync(f, 'utf8');
const walk = (d) => fs.readdirSync(d, { withFileTypes: true }).flatMap((e) => e.isDirectory() ? walk(path.join(d, e.name)) : [path.join(d, e.name)]);
if (!fs.existsSync(DIST)) { console.error('Cartella dist mancante: esegui prima `npm run build`.'); process.exit(1); }

// 1) dati
const D = JSON.parse(read(path.join(ROOT, 'src/data/poems.json'))), P = D.poems;
if (P.length !== 48) warn(`Le poesie sono ${P.length}, non 48.`);
const seen = new Set();
for (const p of P) { if (seen.has(p.slug)) err(`Indirizzo duplicato: ${p.slug}`); seen.add(p.slug); if (!p.testo?.trim() || !p.titolo?.trim()) err(`Poesia ${p.id} senza titolo o testo.`); }

// 2) pagine
const files = walk(DIST), htmls = files.filter((f) => f.endsWith('.html'));
const exists = (u) => { const p = path.join(DIST, u.slice(BASE.length).split('#')[0].split('?')[0]); return fs.existsSync(p) && fs.statSync(p).isFile() || fs.existsSync(path.join(p, 'index.html')); };
let links = 0, bigPage = ['', 0];
for (const f of htmls) {
  const rel = path.relative(DIST, f), h = read(f), isRedirect = /http-equiv="refresh"/.test(h), size = Buffer.byteLength(h);
  if (size > bigPage[1]) bigPage = [rel, size];
  for (const m of h.matchAll(/(?:href|src)="(\/libro-dei-pensieri-muti\/[^"]*)"/g)) { links++; if (!exists(m[1])) err(`${rel}: collegamento rotto ${m[1]}`); }
  if (isRedirect) continue;
  if (!/<html lang="it"/.test(h)) err(`${rel}: manca lang="it"`);
  if (!/<title>[^<]{3,}<\/title>/.test(h)) err(`${rel}: titolo mancante`);
  if (!/<meta name="description" content="[^"]{20,}/.test(h)) err(`${rel}: descrizione mancante o troppo corta`);
  if (!/<link rel="canonical" href="https:\/\/cuordivino\.github\.io\//.test(h)) err(`${rel}: canonical mancante`);
  if (rel !== '404.html' && (h.match(/<h1[ >]/g) || []).length !== 1) err(`${rel}: deve avere un solo <h1>`);
  for (const m of h.matchAll(/<img\b[^>]*>/g)) if (!/\balt=/.test(m[0])) err(`${rel}: immagine senza attributo alt`);
  for (const m of h.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)) { try { JSON.parse(m[1]); } catch { err(`${rel}: JSON-LD non valido`); } }
  if (/noindex/.test(h) === false && !/<meta property="og:image"/.test(h)) err(`${rel}: manca og:image`);
}
for (const need of ['sitemap-index.xml', 'robots.txt', 'manifest.webmanifest', 'sw.js', '404.html']) if (!fs.existsSync(path.join(DIST, need))) err(`File mancante in dist: ${need}`);
if (htmls.length < 100) warn(`Poche pagine generate (${htmls.length}).`);
if (bigPage[1] > 200_000) warn(`Pagina pesante: ${bigPage[0]} (${Math.round(bigPage[1] / 1024)} KB).`);

// 3) cose da completare
const cfg = JSON.parse(read(path.join(ROOT, 'src/data/config.json')));
const noIg = P.filter((p) => !String(p.immagine).startsWith('ig/')).length;
if (noIg) warn(`${noIg} poesie hanno ancora l'immagine segnaposto (mancano quelle di Instagram).`);
const noUrl = P.filter((p) => !p.instagram?.url).length;
if (noUrl) warn(`${noUrl} poesie senza indirizzo del post Instagram.`);
const unv = P.filter((p) => !p.musica?.verificato).length;
if (unv) warn(`${unv} brani non ancora verificati per coerenza.`);
const noDirect = P.filter((p) => !p.musica?.spotify?.includes('/track/') && !p.musica?.youtube?.includes('watch')).length;
if (noDirect) warn(`${noDirect} brani senza link diretto (il lettore integrato non compare).`);
if (!cfg.api) warn('Servizio commenti non collegato (config.api vuoto): i commenti pubblici non sono attivi.');
if (!cfg.email) warn('Nessuna e-mail in config.email.');
const priv = fs.existsSync(path.join(DIST, 'privacy/index.html')) ? read(path.join(DIST, 'privacy/index.html')) : '';
if (/Completa qui/.test(priv)) warn("Informativa privacy da completare (dati del titolare) e da far rivedere.");
const total = files.reduce((s, f) => s + fs.statSync(f).size, 0);

console.log(`\nPagine: ${htmls.length} · collegamenti controllati: ${links} · peso totale: ${(total / 1048576).toFixed(1)} MB`);
if (warns.length) { console.log('\nDa completare (non bloccano):'); warns.forEach((w) => console.log('  - ' + w)); }
if (errors.length) { console.log('\nERRORI (bloccano la pubblicazione):'); errors.slice(0, 40).forEach((e) => console.log('  x ' + e)); if (errors.length > 40) console.log(`  ... altri ${errors.length - 40}`); process.exit(1); }
console.log('\nControllo superato: il sito si può pubblicare.');
