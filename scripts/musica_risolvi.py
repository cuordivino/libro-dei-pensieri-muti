# -*- coding: utf-8 -*-
"""Trova su YouTube il video di ogni brano di scripts/musica.csv e scrive l'indirizzo nella colonna `youtube`.
Serve una chiave gratuita della YouTube Data API v3 (variabile YT_API_KEY). Si esegue da GitHub (Actions > Trova i brani).
Sceglie solo risultati il cui titolo contiene titolo del brano E artista (o il canale e' l'artista / 'Topic'); gli altri restano
vuoti e vanno scelti a mano. Non segna mai un brano come verificato: l'ascolto lo fai tu."""
import os, re, csv, json, urllib.request, urllib.parse
HERE = os.path.dirname(os.path.abspath(__file__)); P = f'{HERE}/musica.csv'
KEY = os.environ.get('YT_API_KEY', ''); BASE = os.environ.get('YT_API_BASE', 'https://www.googleapis.com/youtube/v3')
if not KEY: raise SystemExit('YT_API_KEY non impostata.')
def norm(s):
    s = re.sub(r'\(.*?\)|\[.*?\]', ' ', s.lower()); s = s.replace('ó', 'o').replace('é', 'e').replace('è', 'e').replace('ü', 'u')
    return [w for w in re.findall(r'[a-z0-9]+', s) if w not in {'the', 'of', 'a', 'no', 'in', 'to', 'and', 'feat'}]
def pick(items, brano, artista):
    tb, ta = set(norm(brano)), set(norm(artista))
    best = None
    for it in items:
        sn = it['snippet']; title = set(norm(sn['title'])); ch = set(norm(sn['channelTitle']))
        if not tb or not tb <= title: continue
        if not (ta <= title | ch or len(ta & (title | ch)) >= max(1, len(ta) - 1)): continue
        raw = set(re.findall(r'[a-z]+', (sn['title'] + ' ' + sn['channelTitle']).lower()))
        bad = {'cover', 'tutorial', 'lesson', 'remix', 'live', 'reaction', 'karaoke', 'sheet', 'piano'} & raw if 'piano' not in tb else {'cover', 'tutorial', 'lesson', 'remix', 'live', 'reaction', 'karaoke', 'sheet'} & raw
        score = (not bad) * 4 + ('topic' in ch) * 2 + (ta <= ch) * 1
        if best is None or score > best[0]: best = (score, it)
    return best[1]['id']['videoId'] if best and best[0] >= 4 else None
rows = list(csv.DictReader(open(P, encoding='utf-8'))); n = 0
for r in rows:
    if r['youtube'].strip() or not r['brano'].strip(): continue
    q = urllib.parse.urlencode({'part': 'snippet', 'type': 'video', 'videoEmbeddable': 'true', 'maxResults': 6, 'q': f"{r['brano']} {r['artista']}", 'key': KEY})
    try: items = json.load(urllib.request.urlopen(f'{BASE}/search?{q}', timeout=30)).get('items', [])
    except Exception as e: print('errore', r['id'], e); continue
    vid = pick(items, r['brano'], r['artista'])
    print(f"{r['id']:>3} {r['brano'][:34]:34} -> {vid or 'DA SCEGLIERE A MANO'}")
    if vid: r['youtube'] = f'https://www.youtube.com/watch?v={vid}'; n += 1
w = csv.DictWriter(open(P, 'w', encoding='utf-8', newline=''), rows[0].keys()); w.writeheader(); w.writerows(rows)
print(f'trovati {n} brani')
