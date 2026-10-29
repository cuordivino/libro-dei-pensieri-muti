# -*- coding: utf-8 -*-
"""Sincronizza i post di Instagram (Instagram API con accesso Instagram) con il sito.
Variabili: IG_TOKEN (token a lunga durata)  [IG_API_BASE solo per le prove].
Ogni esecuzione: scarica l'elenco dei post, abbina i nuovi alle poesie (punteggio di affidabilità),
tiene stabili gli abbinamenti già fatti, rispetta le correzioni manuali in scripts/instagram-links.csv,
scrive src/data/instagram-map.json e src/data/instagram-posts.json e salva le immagini."""
import os, sys, re, json, csv, io, difflib, urllib.request, urllib.parse, datetime
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
TOKEN = os.environ.get('IG_TOKEN', '').strip(); BASE = os.environ.get('IG_API_BASE', 'https://graph.instagram.com')
SOGLIA, MAX_LIBERI = 0.35, 24
if not TOKEN: print('IG_TOKEN non impostato: sincronizzazione saltata.'); sys.exit(0)
get = lambda u: urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'pensieri-muti-sync'}), timeout=60).read()

posts, url = [], f'{BASE}/me/media?' + urllib.parse.urlencode({'fields': 'id,caption,media_type,media_url,thumbnail_url,permalink,timestamp', 'limit': 50, 'access_token': TOKEN})
while url:
    d = json.loads(get(url)); posts += d.get('data', []); url = d.get('paging', {}).get('next')
print(len(posts), 'post letti da Instagram')

poems = json.load(open(f'{ROOT}/src/data/poems.json', encoding='utf-8'))['poems']
mp = f'{ROOT}/src/data/instagram-map.json'; old = json.load(open(mp, encoding='utf-8')) if os.path.exists(mp) else {}
norm = lambda s: re.sub(r'[^a-zà-ù0-9 ]+', ' ', (s or '').lower()).split()
canon = lambda u: (u or '').split('?')[0].rstrip('/').lower()
def score(cap, p):
    a, b = norm(cap), norm(p['testo'] + ' ' + p['titolo'])
    if not a: return 0.0
    sa, sb = set(a), set(b)
    seq = difflib.SequenceMatcher(None, ' '.join(a)[:400], ' '.join(b)[:400]).ratio()
    bonus = 0.15 if norm(p['titolo']) and ' '.join(norm(p['titolo'])) in ' '.join(a) else 0
    return min(1.0, 0.45 * len(sa & sb) / len(sa) + 0.25 * len(sa & sb) / len(sa | sb) + 0.3 * seq + bonus)

by_id = {p['id']: p for p in poems}; assign = {}      # post_id -> (poem_id, score, stato)
csvp = f'{HERE}/instagram-links.csv'; manual = {}
if os.path.exists(csvp):
    for r in csv.DictReader(open(csvp, encoding='utf-8')):
        if r.get('url', '').strip(): manual[canon(r['url'])] = int(r['id'])
for po in posts:                                            # 1) correzioni manuali
    if canon(po['permalink']) in manual: assign[po['id']] = (manual[canon(po['permalink'])], 1.0, 'manuale')
used = {v[0] for v in assign.values()}
for pid, v in old.items():                                  # 2) abbinamenti già fatti restano stabili
    if v.get('post_id') in {p['id'] for p in posts} and v['post_id'] not in assign and int(pid) not in used:
        assign[v['post_id']] = (int(pid), v['punteggio'], v['stato']); used.add(int(pid))
pairs = sorted(((score(po.get('caption'), p), po['id'], p['id']) for po in posts if po['id'] not in assign for p in poems if p['id'] not in used), reverse=True)
for s, post_id, pid in pairs:                               # 3) nuovi post: abbinamento solo sopra soglia
    if s < SOGLIA or post_id in assign or pid in used: continue
    assign[post_id] = (pid, round(s, 2), 'sicuro' if s >= 0.6 else 'da verificare'); used.add(pid)

os.makedirs(f'{ROOT}/public/images/ig', exist_ok=True)
def fetch_img(po):
    u = po.get('thumbnail_url') if po['media_type'] == 'VIDEO' else po.get('media_url')
    return Image.open(io.BytesIO(get(u))).convert('RGB') if u else None
def save(im, base, big):
    if big: b = im.copy(); b.thumbnail((1600, 2000)); b.save(f'{ROOT}/public/images/ig/{base}.jpg', quality=85, optimize=True, progressive=True)
    s = im.copy(); s.thumbnail((800, 1000)); s.save(f'{ROOT}/public/images/ig/{base}-800.webp', quality=80)

newmap, out_posts, liberi = {}, [], 0
for po in sorted(posts, key=lambda x: x['timestamp'], reverse=True):
    a = assign.get(po['id']); data = po['timestamp'][:10]; cap = (po.get('caption') or '')
    item = {'id': po['id'], 'url': po['permalink'], 'data': data, 'tipo': po['media_type'], 'didascalia': cap[:280], 'poesia': a[0] if a else None, 'immagine': None}
    try:
        if a:
            pid = a[0]; fn = f'{pid:02d}'
            if not (old.get(str(pid), {}).get('post_id') == po['id'] and os.path.exists(f'{ROOT}/public/images/ig/{fn}.jpg')):
                im = fetch_img(po); save(im, fn, True) if im else None
            item['immagine'] = f'ig/{fn}-800.webp'
            newmap[str(pid)] = {'post_id': po['id'], 'url': po['permalink'], 'data': data, 'didascalia': cap[:280], 'punteggio': a[1], 'stato': a[2], 'tipo': po['media_type']}
        elif liberi < MAX_LIBERI:
            fn = f"post-{po['id']}"
            if not os.path.exists(f'{ROOT}/public/images/ig/{fn}-800.webp'):
                im = fetch_img(po); save(im, fn, False) if im else None
            item['immagine'] = f'ig/{fn}-800.webp'; liberi += 1
    except Exception as e: print('immagine non scaricata per', po['id'], e)
    out_posts.append(item)
json.dump(newmap, open(mp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(out_posts, open(f'{ROOT}/src/data/instagram-posts.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
# elenco di controllo per le correzioni manuali
old_urls = {}
if os.path.exists(csvp): old_urls = {r['id']: r['url'] for r in csv.DictReader(open(csvp, encoding='utf-8'))}
with open(csvp, 'w', encoding='utf-8', newline='') as f:
    w = csv.writer(f); w.writerow(['id', 'titolo', 'url', 'stato'])
    for p in poems: w.writerow([p['id'], p['titolo'], old_urls.get(str(p['id']), ''), newmap.get(str(p['id']), {}).get('stato', 'non abbinato')])
nuovi = [k for k in newmap if k not in old or old[k].get('post_id') != newmap[k]['post_id']]
print(f"abbinate {len(newmap)}/{len(poems)} poesie; nuove oggi: {nuovi}; post non abbinati: {sum(1 for p in out_posts if p['poesia'] is None)}")
