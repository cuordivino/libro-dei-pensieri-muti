# -*- coding: utf-8 -*-
"""Integra il quaderno di testi (txt) nel sito: scarta separatori, doppioni (si tiene SEMPRE il testo gia' presente),
poesie firmate da altri e unisce le parti di "Spettacolo teatrale".  Uso: python3 scripts/integra_materiale.py quaderno.txt
Scrive src/data/integrazioni.json (nuove poesie), aggiunge a src/data/escluse.json.  Poi: npm run data"""
import sys, re, json, os, difflib, unicodedata
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
if len(sys.argv) < 2: sys.exit(__doc__)
norm = lambda s: ' '.join(re.sub(r'[^a-z0-9 ]+', ' ', unicodedata.normalize('NFD', s.lower()).encode('ascii', 'ignore').decode()).split())
t = open(sys.argv[1], encoding='utf-8').read().replace('\r\n', '\n').replace('\r', '\n')
blocks = [b.strip('\n ') for b in re.split(r'\n-{10,}[ \t]*\n', t)]
blocks = [b for b in blocks if b.strip() and not re.fullmatch(r'[-\s_.]*', b)]
def sentence(s):
    s = re.sub(r'[_]+', ' ', s).strip(' ,;:.…-"“”'); s = re.sub(r'\s+', ' ', s)
    return s[:1].upper() + s[1:].lower() if s.isupper() or s.islower() else s[:1].upper() + s[1:]
raw = []
for b in blocks:
    ls = [l.rstrip() for l in b.split('\n')]
    first = ls[0].strip()
    if first.startswith('Atto ') or first.startswith('Atto'): raw.append({'titolo': 'Spettacolo teatrale', 'testo': b, 'atto': True}); continue
    if len(ls) > 1 and not ls[1].strip() and len(first) <= 60 and first not in ('.', '') and not first.endswith((',', ';')): titolo, body = first, '\n'.join(ls[2:]).strip()
    elif first.isupper() and len(first) <= 60 and len(ls) > 1: titolo, body = first, '\n'.join(ls[1:]).strip()
    else:
        words = first.rstrip(' ,;.').split(); titolo, body = ' '.join(words[:6]), b.strip()
        if first == '.': l2 = [l for l in ls[1:] if l.strip()]; w = l2[0].split(); titolo = ' '.join(w[:6]); body = '\n'.join(ls[1:]).strip()
    raw.append({'titolo': sentence(titolo), 'testo': re.sub(r'\n{3,}', '\n\n', body)})
# unisco "Spettacolo teatrale" (Atto 1, Atto 2, Atto finale) in un'unica opera
atti = [r for r in raw if r['titolo'].lower().startswith(('spettacolo teatrale', 'atto finale'))]
raw = [r for r in raw if r not in atti]
if atti:
    parts = []
    for a_ in atti:
        tx = re.sub(r'\n?\s*segue\s*\.+\s*$', '', a_['testo'].strip(), flags=re.I)
        parts.append(('Atto finale\n\n' + tx) if a_['titolo'].lower().startswith('atto finale') else tx)
    raw.append({'titolo': 'Spettacolo teatrale', 'testo': '\n\n'.join(parts)})
ex = json.load(open(f'{ROOT}/src/data/poems.json', encoding='utf-8'))['poems']
exk = [norm(p['testo'])[:500] for p in ex]
ext = {norm(p['titolo']) for p in ex}
ALTRI = {'elevazione': 'Charles Baudelaire (Élévation, in traduzione)'}
nuove, escluse, seen = [], [], []
for r in raw:
    k = norm(r['testo'])[:500]
    if r['titolo'].lower() in ALTRI: escluse.append({'titolo': r['titolo'], 'autore': ALTRI[r['titolo'].lower()], 'motivo': 'poesia di un altro autore', 'data': None}); continue
    if norm(r['titolo']) in ext or any(difflib.SequenceMatcher(None, k, e).ratio() >= 0.8 for e in exk): continue   # doppione (anche solo per titolo): si tiene l'esistente
    if any(difflib.SequenceMatcher(None, k, s).ratio() >= 0.9 for s in seen): continue          # doppione interno al quaderno
    seen.append(k); nuove.append(r)
cnt = {}
for r in nuove:                                                                                   # titoli uguali: distinguo
    n = r['titolo'].lower(); cnt[n] = cnt.get(n, 0) + 1
    if cnt[n] > 1: r['titolo'] += ' (' + 'I' * cnt[n] + ')'
start = max([p['id'] for p in ex] + [99]) + 1
out = [{'id': start + i, 'titolo': r['titolo'], 'testo': r['testo']} for i, r in enumerate(nuove)]
json.dump(out, open(f'{ROOT}/src/data/integrazioni.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
ep = f'{ROOT}/src/data/escluse.json'; esc = json.load(open(ep, encoding='utf-8')) if os.path.exists(ep) else []
esc = [e for e in esc if e.get('autore') not in ALTRI.values()] + escluse
json.dump(esc, open(ep, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'{len(out)} poesie nuove dal quaderno; escluse aggiunte: {len(escluse)}')
