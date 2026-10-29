# -*- coding: utf-8 -*-
"""Importa i post Instagram dall'esportazione ufficiale e li abbina alle poesie.

Uso:  python3 scripts/import_instagram.py  <cartella-esportazione>  [--soglia 0.35]
Poi:  npm run data

1. Instagram → Impostazioni → Centro gestione account → Le tue informazioni e autorizzazioni
   → Scarica le tue informazioni → Post, formato JSON, qualità massima.
2. Decomprimi lo zip e passa la cartella a questo script.
Scrive: public/images/ig/NN.jpg (1600px) e NN-800.webp, src/data/instagram-map.json,
        scripts/instagram-links.csv (da completare con gli indirizzi dei post).
Abbinamento: somiglianza tra didascalia e testo/titolo della poesia. Nessun abbinamento è
forzato: sotto soglia il post resta "non abbinato" e va assegnato a mano nel CSV."""
import sys, os, re, json, glob, csv, difflib, datetime, shutil
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
args = [a for a in sys.argv[1:] if not a.startswith('--')]
soglia = float(sys.argv[sys.argv.index('--soglia') + 1]) if '--soglia' in sys.argv else 0.35
if not args: sys.exit(__doc__)
exp = args[0]

def fix(s):  # l'esportazione Instagram salva l'UTF-8 come latin-1
    try: return s.encode('latin1').decode('utf8')
    except Exception: return s
norm = lambda s: re.sub(r'[^a-zà-ù0-9 ]+', ' ', s.lower()).split()

files = glob.glob(f'{exp}/**/posts_*.json', recursive=True)
if not files: sys.exit('Nessun posts_*.json trovato nella cartella.')
posts = []
for f in files:
    for it in json.load(open(f, encoding='utf-8')):
        media = it.get('media', [])
        if not media: continue
        cap = fix(it.get('title') or media[0].get('title') or '')
        ts = it.get('creation_timestamp') or media[0].get('creation_timestamp') or 0
        uris = [m['uri'] for m in media if re.search(r'\.(jpe?g|png|webp)$', m['uri'], re.I)]
        if uris: posts.append({'cap': cap, 'ts': ts, 'uris': uris})
print(len(posts), 'post con immagini trovati')

poems = json.load(open(f'{ROOT}/src/data/poems.json', encoding='utf-8'))['poems']
def score(cap, p):
    a, b = norm(cap), norm(p['testo'] + ' ' + p['titolo'])
    if not a: return 0.0
    sa, sb = set(a), set(b)
    jac = len(sa & sb) / max(1, len(sa | sb))
    cover = len(sa & sb) / max(1, len(sa))            # quanta didascalia è testo della poesia
    seq = difflib.SequenceMatcher(None, ' '.join(a)[:400], ' '.join(b)[:400]).ratio()
    bonus = 0.15 if norm(p['titolo']) and ' '.join(norm(p['titolo'])) in ' '.join(a) else 0
    return min(1.0, 0.45 * cover + 0.25 * jac + 0.3 * seq + bonus)

pairs = sorted(((score(po['cap'], p), i, p['id']) for i, po in enumerate(posts) for p in poems), reverse=True)
used_post, used_poem, match = set(), set(), {}
for s, i, pid in pairs:
    if s < soglia or i in used_post or pid in used_poem: continue
    used_post.add(i); used_poem.add(pid); match[pid] = (i, s)

os.makedirs(f'{ROOT}/public/images/ig', exist_ok=True)
out = {}
for pid, (i, s) in sorted(match.items()):
    po = posts[i]; src = os.path.join(exp, po['uris'][0])
    if not os.path.exists(src):
        hit = glob.glob(f'{exp}/**/{os.path.basename(po["uris"][0])}', recursive=True)
        if not hit: print('immagine mancante per poesia', pid); continue
        src = hit[0]
    im = Image.open(src).convert('RGB'); im.thumbnail((1600, 2000))
    im.save(f'{ROOT}/public/images/ig/{pid:02d}.jpg', quality=85, optimize=True, progressive=True)
    sm = im.copy(); sm.thumbnail((800, 1000)); sm.save(f'{ROOT}/public/images/ig/{pid:02d}-800.webp', quality=80)
    out[str(pid)] = {'data': datetime.datetime.fromtimestamp(po['ts']).strftime('%Y-%m-%d') if po['ts'] else None,
                     'didascalia': po['cap'][:280], 'punteggio': round(s, 2),
                     'stato': 'sicuro' if s >= 0.6 else 'da verificare', 'immagini': len(po['uris'])}
json.dump(out, open(f'{ROOT}/src/data/instagram-map.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

csvp = f'{HERE}/instagram-links.csv'
old = {}
if os.path.exists(csvp):
    for r in csv.DictReader(open(csvp, encoding='utf-8')): old[r['id']] = r['url']
with open(csvp, 'w', encoding='utf-8', newline='') as f:
    w = csv.writer(f); w.writerow(['id', 'titolo', 'url', 'stato'])
    for p in poems: w.writerow([p['id'], p['titolo'], old.get(str(p['id']), ''), out.get(str(p['id']), {}).get('stato', 'non abbinato')])
print(f'abbinate {len(out)}/{len(poems)} poesie ({sum(v["stato"]=="sicuro" for v in out.values())} sicure).')
print('Non abbinate:', [p['id'] for p in poems if str(p['id']) not in out])
print('Ora: apri scripts/instagram-links.csv, incolla gli indirizzi dei post, poi  npm run data')
