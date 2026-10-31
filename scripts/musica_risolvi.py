# -*- coding: utf-8 -*-
"""Trova su YouTube il video di ogni brano di scripts/musica.csv e scrive l'indirizzo nella colonna `youtube`.
Due modi: con YT_API_KEY usa la YouTube Data API; senza chiave usa yt-dlp (ricerca pubblica). In entrambi i casi sceglie
solo risultati il cui titolo contiene brano E artista (o il canale e' l'artista / 'Topic'), scarta cover, live e tutorial,
e controlla che il video sia incorporabile (oEmbed). Non segna mai un brano come verificato: l'ascolto lo fai tu."""
import os, re, csv, json, urllib.request, urllib.parse
HERE = os.path.dirname(os.path.abspath(__file__)); P = f'{HERE}/musica.csv'
KEY = os.environ.get('YT_API_KEY', ''); BASE = os.environ.get('YT_API_BASE', 'https://www.googleapis.com/youtube/v3')
FIX = os.environ.get('YT_FIXTURE')  # solo per le prove
def norm(s):
    s = re.sub(r'\(.*?\)|\[.*?\]', ' ', s.lower()); s = s.replace('\u00f3', 'o').replace('\u00e9', 'e').replace('\u00e8', 'e').replace('\u00fc', 'u')
    return [w for w in re.findall(r'[a-z0-9]+', s) if w not in {'the', 'of', 'a', 'no', 'in', 'to', 'and', 'feat'}]
def ranked(items, brano, artista):
    """ID dei risultati accettabili, dal migliore al peggiore."""
    tb, ta = set(norm(brano)), set(norm(artista)); out = []
    for it in items:
        sn = it['snippet']; title = set(norm(sn['title'])); ch = set(norm(sn['channelTitle']))
        if not tb or not tb <= title: continue
        if not (ta <= title | ch or len(ta & (title | ch)) >= max(1, len(ta) - 1)): continue
        raw = set(re.findall(r'[a-z]+', (sn['title'] + ' ' + sn['channelTitle']).lower()))
        bad = {'cover', 'tutorial', 'lesson', 'remix', 'live', 'reaction', 'karaoke', 'sheet', 'lyrics'} & raw
        if 'piano' not in tb: bad |= {'piano'} & raw
        score = (not bad) * 4 + ('topic' in ch) * 2 + (ta <= ch) * 1
        if score >= 4: out.append((score, it['id']['videoId']))
    return [v for _, v in sorted(out, key=lambda x: -x[0])]
def search(q):
    if FIX:
        d = json.load(open(FIX, encoding='utf-8')); k = next((k for k in d if k in q.lower()), None); return d.get(k, [])
    if KEY:
        u = urllib.parse.urlencode({'part': 'snippet', 'type': 'video', 'videoEmbeddable': 'true', 'maxResults': 8, 'q': q, 'key': KEY})
        return json.load(urllib.request.urlopen(f'{BASE}/search?{u}', timeout=30)).get('items', [])
    import yt_dlp
    with yt_dlp.YoutubeDL({'quiet': True, 'extract_flat': True, 'skip_download': True, 'no_warnings': True}) as y:
        es = (y.extract_info(f'ytsearch8:{q}', download=False) or {}).get('entries', [])
    return [{'id': {'videoId': e['id']}, 'snippet': {'title': e.get('title') or '', 'channelTitle': e.get('channel') or e.get('uploader') or ''}} for e in es if e and e.get('id')]
def embeddable(vid):
    if FIX: return True
    try:
        u = 'https://www.youtube.com/oembed?format=json&url=' + urllib.parse.quote(f'https://www.youtube.com/watch?v={vid}')
        return urllib.request.urlopen(u, timeout=20).status == 200
    except Exception: return False
rows = list(csv.DictReader(open(P, encoding='utf-8'))); n = 0; errori = 0
for r in rows:
    if r['youtube'].strip() or not r['brano'].strip(): continue
    try: items = search(f"{r['brano']} {r['artista']}")
    except Exception as e: print('errore', r['id'], str(e)[:90]); errori += 1; continue
    vid = next((v for v in ranked(items, r['brano'], r['artista']) if embeddable(v)), None)
    print(f"{r['id']:>3} {r['brano'][:34]:34} -> {vid or 'DA SCEGLIERE A MANO'}")
    if vid: r['youtube'] = f'https://www.youtube.com/watch?v={vid}'; n += 1
w = csv.DictWriter(open(P, 'w', encoding='utf-8', newline=''), rows[0].keys()); w.writeheader(); w.writerows(rows)
print(f'trovati {n} brani; errori di ricerca: {errori}')
