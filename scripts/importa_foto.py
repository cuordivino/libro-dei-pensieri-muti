# -*- coding: utf-8 -*-
"""Importa foto nominate con il TITOLO (o l'inizio) della poesia: "Il lembo.jpg", "36 - Attimo sfuggente.jpg".
Uso: python3 scripts/importa_foto.py <cartella-foto>   poi  npm run data
Abbina ogni file alla poesia piu' simile; sotto 0.9 di somiglianza NON la importa e la elenca da controllare.
Salva public/images/foto/ID.jpg (max 1200x1500) e ID-800.webp. Le foto hanno la precedenza sulle immagini generate."""
import sys, re, os, json, glob, difflib, unicodedata
from PIL import Image, ImageOps
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
if len(sys.argv) < 2: sys.exit(__doc__)
norm = lambda s: ' '.join(re.sub(r'[^a-z0-9 ]+', ' ', unicodedata.normalize('NFD', s.lower().replace('’', "'")).encode('ascii', 'ignore').decode()).split())
P = json.load(open(f'{ROOT}/src/data/poems.json', encoding='utf-8'))['poems']
os.makedirs(f'{ROOT}/public/images/foto', exist_ok=True); ok, dubbi = 0, []
for f in sorted(glob.glob(os.path.join(sys.argv[1], '*.*'))):
    if not f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')): continue
    base = os.path.splitext(os.path.basename(f))[0]; m = re.match(r'^(\d+)\s*-\s*(.*)$', base)
    if m: pid, sc = int(m.group(1)), 1.0
    else:
        b = norm(base.replace('(ii)', '(II)')); best = (0, None)
        for p in P:
            t, x = norm(p['titolo']), norm(p['testo'])[:len(b) + 25]
            s = 1.0 if t == b else max(difflib.SequenceMatcher(None, b, t).ratio(), difflib.SequenceMatcher(None, b, x[:len(b)]).ratio() * .97)
            if s > best[0]: best = (s, p)
        sc, pid = best[0], best[1]['id']
    if sc < 0.9: dubbi.append((base, pid, round(sc, 2))); continue
    im = ImageOps.exif_transpose(Image.open(f)).convert('RGB'); a = im.copy(); a.thumbnail((1200, 1500)); a.save(f'{ROOT}/public/images/foto/{pid}.jpg', quality=86, optimize=True, progressive=True)
    b8 = im.copy(); b8.thumbnail((800, 1000)); b8.save(f'{ROOT}/public/images/foto/{pid}-800.webp', quality=80); ok += 1
print(f'importate {ok} foto; da controllare: {dubbi}')
