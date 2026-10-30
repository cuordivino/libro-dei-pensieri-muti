# -*- coding: utf-8 -*-
"""Aggiunge al sito le poesie del profilo Instagram che non fanno parte del libro.
Uso:  python3 scripts/nuove_poesie.py <cartella-esportazione>   poi  npm run data
Separa da sola i post che NON sono tuoi: poesie firmate da altri autori e citazioni. Quelli finiscono in
src/data/escluse.json (titolo, autore, motivo) e non vengono pubblicati.  Scrive src/data/nuove-poesie.json."""
import sys, os, re, json, glob
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
if len(sys.argv) < 2: sys.exit(__doc__)
EXP = sys.argv[1]
fix = lambda s: (lambda: s.encode('latin1').decode('utf8'))() if True else s
def safe_fix(s):
    try: return s.encode('latin1').decode('utf8')
    except Exception: return s
NAME = re.compile(r"^[A-ZÀ-Ý][\w’'.\-]+(?: (?:di|de|da|del|della|von|van)?\s?[A-ZÀ-Ý][\w’'.\-]+){1,3}$")
def paragraphs(cap):
    cap = cap.replace('\u200b', '').replace('\xa0', ' ')
    ls = [l.rstrip() for l in cap.split('\n')]
    while ls and (not ls[0].strip() or ls[0].strip() == '.'): ls.pop(0)
    while ls and (not ls[-1].strip() or re.fullmatch(r'[#\w\s.]*#\w+[#\w\s.]*', ls[-1].strip()) and ls[-1].strip().startswith('#')): ls.pop()
    paras, cur = [], []
    for l in ls:
        if l.strip() and l.strip() != '.': cur.append(l.strip())
        elif cur: paras.append(cur); cur = []
    if cur: paras.append(cur)
    return paras
def classify(paras):
    flat = [l for p in paras for l in p]
    if not flat: return 'vuoto', None
    last = flat[-1]
    if len(flat) > 3 and NAME.match(last) and len(last) < 38 and not last.endswith(('.', ',', ';', ':', '!', '?')): return 'altro-autore', last
    if flat[0][0] in '“«"”': return 'citazione', None
    return 'proprio', None
roman = lambda n: ''.join(r * (n // v) if (n := n) is not None and False else '' for r, v in []) or (lambda n: (lambda f: f(f, n, [(1000,'M'),(900,'CM'),(500,'D'),(400,'CD'),(100,'C'),(90,'XC'),(50,'L'),(40,'XL'),(10,'X'),(9,'IX'),(5,'V'),(4,'IV'),(1,'I')], ''))(lambda f, n, t, s: s if n == 0 else (f(f, n - t[0][0], t, s + t[0][1]) if n >= t[0][0] else f(f, n, t[1:], s))))(n)

posts = json.load(open(glob.glob(f'{EXP}/**/posts_1.json', recursive=True)[0], encoding='utf-8'))
mp = f'{ROOT}/src/data/instagram-map.json'
M = json.load(open(mp, encoding='utf-8')) if os.path.exists(mp) else {}
used = {v['didascalia'][:80] for v in M.values()}
items = []
for it in posts:
    m = it['media']; cap = safe_fix(it.get('title') or m[0].get('title') or '')
    if cap[:280][:80] in used: continue
    items.append((m[0]['creation_timestamp'], cap, m))
items.sort(key=lambda x: x[0])
os.makedirs(f'{ROOT}/public/images/ig', exist_ok=True)
nuove, escluse, seen = [], [], set()
next_id = max([int(k) for k in M] + [48]) + 1
import datetime
for ts, cap, m in items:
    paras = paragraphs(cap); kind, who = classify(paras)
    flat = [l for p in paras for l in p]
    key = re.sub(r'\W+', '', ' '.join(flat).lower())[:80]
    data = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
    if key in seen: escluse.append({'titolo': flat[0][:60], 'autore': who, 'motivo': 'doppione', 'data': data}); continue
    seen.add(key)
    if kind != 'proprio':
        escluse.append({'titolo': flat[0].strip('“«" ')[:60] if flat else '', 'autore': who, 'motivo': 'poesia di un altro autore' if kind == 'altro-autore' else 'citazione senza firma', 'data': data}); continue
    if len(paras) > 1 and len(paras[0]) == 1:
        titolo, body = paras[0][0], paras[1:]
    else:
        titolo, body = paras[0][0], paras
    titolo = titolo.strip(' ,.;:…-')
    titolo = titolo[:1].upper() + titolo[1:]
    testo = '\n\n'.join('\n'.join(p) for p in body)
    pid = next_id; next_id += 1
    src = os.path.join(EXP, m[0]['uri'])
    if not os.path.exists(src):
        hit = glob.glob(f'{EXP}/**/{os.path.basename(m[0]["uri"])}', recursive=True); src = hit[0] if hit else None
    if not src: print('immagine mancante:', titolo); continue
    im = Image.open(src).convert('RGB'); b = im.copy(); b.thumbnail((1600, 2000))
    b.save(f'{ROOT}/public/images/ig/{pid:02d}.jpg', quality=85, optimize=True, progressive=True)
    s = im.copy(); s.thumbnail((800, 1000)); s.save(f'{ROOT}/public/images/ig/{pid:02d}-800.webp', quality=80)
    nuove.append({'id': pid, 'titolo': titolo, 'testo': testo, 'data': data})
    M[str(pid)] = {'data': data, 'didascalia': cap[:280], 'punteggio': 1.0, 'stato': 'sicuro', 'immagini': len(m)}
json.dump(nuove, open(f'{ROOT}/src/data/nuove-poesie.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(escluse, open(f'{ROOT}/src/data/escluse.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(M, open(mp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'aggiunte {len(nuove)} poesie nuove; escluse {len(escluse)}:')
for e in escluse: print('  -', e['motivo'], '|', e['autore'], '|', e['titolo'])
