# -*- coding: utf-8 -*-
"""Migra poems.source.json -> src/data/poems.json con temi, parole chiave, citazione, link musicali, correlate.
I campi marcati `auto` sono proposte automatiche: correggili a mano in src/data/overrides.json."""
import json, re, os, csv, urllib.parse as up
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
src = json.load(open(f'{HERE}/poems.source.json', encoding='utf-8'))
ovr_path = f'{ROOT}/src/data/overrides.json'
ovr = json.load(open(ovr_path, encoding='utf-8')) if os.path.exists(ovr_path) else {}

THEMES = {
 'memoria': r'\bricord|\bmemori|\bpassat|\bieri\b|\bnostalg|\bricordi',
 'amore': r'\bamor|\bbaci|\bcuore|\blabbra|\babbracc|\bdesider|\bbram',
 'perdita': r'\bperdu|\bperd[oe]|\blutto|\bmort|\baddio|\bsvanis|\bcadut|\bcade',
 'silenzio': r'\bsilenz|\bmut[oai]\b|\btaci|\bquiet|\bzitt',
 'assenza': r'\bassenz|\bvuot|\bniente|\bnulla\b|\bmanc|\blontan|\bindifferen',
 'tempo': r'\btemp[oi]\b|\battim|\banni\b|\bsera\b|\beterno|\bistante',
 'mare': r'\bmare\b|\bond[ae]\b|\bacqua|\briva\b|\bnaufrag|\bannego|\bmarin|\bimmers',
 'notte': r'\bnott|\bbuio|\bombra|\bluna\b|\bstell|\btenebr|\boscur|\bnebbia',
 'attesa': r'\battend|\battes|\baspett|\bsperan|\bancora\b',
 'rinascita': r'\brinasc|\briaffior|\brisorg|\balba\b|\bgermogl|\britrov|\briassapor|\bluce|\blevigh',
}
THEME_LABEL = {k: k.capitalize() for k in THEMES}
EMO = {'nuovi': [], 'ombra': ['malinconia','apatia','abisso'], 'ardore': ['desiderio','furore','estasi'],
       'maschera': ['disprezzo','ribellione','ironia'], 'quiete': ['pace','ritrovo','consolazione']}
STOP = set('come sono nella nelle degli delle dello della tutti tutto questo questa quello quella ancora anche senza dentro verso quando mentre perché poi così dove ogni molto altro altra altri sotto sopra fino tra fra più mio mia miei mie suo sua loro cosa solo ormai'.split())
slug = lambda s: re.sub(r'[^a-z0-9]+','-', s.lower().replace('à','a').replace('è','e').replace('é','e').replace('ì','i').replace('ò','o').replace('ù','u')).strip('-')
def words(t): return re.findall(r"[a-zàèéìòù]{5,}", t.lower())

igp = f'{ROOT}/src/data/instagram-map.json'
igmap = json.load(open(igp, encoding='utf-8')) if os.path.exists(igp) else {}
csvp = f'{HERE}/instagram-links.csv'
iglinks = {r['id']: r['url'].strip() for r in csv.DictReader(open(csvp, encoding='utf-8'))} if os.path.exists(csvp) else {}
if not os.path.exists(csvp):
    with open(csvp, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f); w.writerow(['id', 'titolo', 'url', 'stato'])
        for p in src['poems']: w.writerow([p['id'], p['title'].lower().capitalize(), '', 'non abbinato'])
mcsv = f'{HERE}/musica.csv'
mus = {r['id']: r for r in csv.DictReader(open(mcsv, encoding='utf-8'))} if os.path.exists(mcsv) else {}

def roman(n):
    out = ''
    for v, r in [(1000,'M'),(900,'CM'),(500,'D'),(400,'CD'),(100,'C'),(90,'XC'),(50,'L'),(40,'XL'),(10,'X'),(9,'IX'),(5,'V'),(4,'IV'),(1,'I')]:
        while n >= v: out += r; n -= v
    return out
nup = f'{ROOT}/src/data/nuove-poesie.json'
nuove = json.load(open(nup, encoding='utf-8')) if os.path.exists(nup) else []
all_src = list(src['poems']) + [{'id': n['id'], 'title': n['titolo'], 'number': roman(n['id']), 'sectionTitle': 'Versi nuovi', 'macroMoodKey': 'nuovi',
    'macroMood': 'I Versi Nuovi', 'moodPrimary': '', 'moodSense': '', 'text': n['testo'], 'image': 'images/poesia_1.jpg', 'musicTrack': '', 'musicArtist': ''} for n in nuove]
poems = []
for p in all_src:
    t = p['text']; low = t.lower()
    sc = {k: len(re.findall(rx, low)) for k, rx in THEMES.items()}
    themes = [k for k, v in sorted(sc.items(), key=lambda x: -x[1]) if v][:3] or ['silenzio']
    kw = [w for w, _ in Counter(w for w in words(t) if w not in STOP).most_common(6)][:5]
    lines = [l.strip() for l in t.split('\n') if 25 <= len(l.strip()) <= 80]
    quote = max(lines, key=lambda l: sum(len(re.findall(THEMES[th], l.lower())) for th in themes) + len(l)/200) if lines else t.split('\n')[-1]
    q = up.quote(f"{p['musicTrack']} {p['musicArtist']}")
    d = {
      'id': p['id'], 'slug': f"{p['id']:02d}-{slug(p['title'])}", 'numero': p['number'], 'titolo': p['title'].lower().capitalize(),
      'sezione': p['sectionTitle'].capitalize(), 'mood': p['macroMoodKey'], 'moodNome': p['macroMood'],
      'statoAnimo': p['moodPrimary'], 'senso': p['moodSense'] or None, 'testo': t,
      'immagine': p['image'].split('/')[-1], 'data': None,
      'temi': themes, 'emozioni': EMO[p['macroMoodKey']], 'parole': kw, 'citazione': quote.strip(),
      'musica': ({'brano': p['musicTrack'], 'artista': p['musicArtist'], 'verificato': False,
                 'spotify': f'https://open.spotify.com/search/{q}', 'youtube': f'https://music.youtube.com/search?q={q}',
                 'apple': f'https://music.apple.com/it/search?term={q}', 'soundcloud': f'https://soundcloud.com/search?q={q}', 'audio': None}
                 if p['musicTrack'] else {'brano': '', 'artista': '', 'verificato': False, 'spotify': '', 'youtube': '', 'apple': '', 'soundcloud': '', 'audio': None}),
      'instagram': None, 'auto': ['temi','parole','citazione'],
    }
    ig = igmap.get(str(p['id']))
    if ig:
        d['immagine'] = f"ig/{p['id']:02d}.jpg"; d['miniatura'] = f"ig/{p['id']:02d}-800.webp"; d['data'] = ig['data']
        d['instagram'] = {'url': iglinks.get(str(p['id'])) or ig.get('url') or None, 'punteggio': ig['punteggio'], 'stato': ig['stato'], 'didascalia': ig['didascalia']}
    elif iglinks.get(str(p['id'])):
        d['instagram'] = {'url': iglinks[str(p['id'])], 'punteggio': None, 'stato': 'manuale', 'didascalia': None}
    d.setdefault('miniatura', d['immagine'])
    m = mus.get(str(p['id']))
    if m:
        for k in ('spotify', 'youtube', 'apple', 'soundcloud'):
            if m.get(k, '').strip(): d['musica'][k] = m[k].strip()
        if m.get('brano', '').strip(): d['musica']['brano'] = m['brano'].strip()
        if m.get('artista', '').strip(): d['musica']['artista'] = m['artista'].strip()
        d['musica']['verificato'] = m.get('verificato', '').strip().lower() in ('si', 'sì', 'x', '1')
        d['musica']['perche'] = m.get('perche', '').strip() or None
    d.update(ovr.get(str(p['id']), {}))
    mm = d['musica']; qq = up.quote(f"{mm['brano']} {mm['artista']}".strip())
    mm['cerca'] = ({'spotify': f'https://open.spotify.com/search/{qq}', 'youtube': f'https://music.youtube.com/search?q={qq}',
                    'apple': f'https://music.apple.com/it/search?term={qq}', 'soundcloud': f'https://soundcloud.com/search?q={qq}'} if mm['brano'] else None)
    poems.append(d)

feat = lambda p: {'t:'+x for x in p['temi']} | {'t:'+x for x in p['temi']} | set(p['parole']) | {p['mood']}
for p in poems:
    f = feat(p)
    s = sorted(((len(f & feat(o)) / len(f | feat(o)), o['id']) for o in poems if o['id'] != p['id']), reverse=True)
    p['correlate'] = [i for _, i in s[:3]]

m = src['meta']
meta = {'titolo': m['title'].title().replace('Dei','dei'), 'sottotitolo': m['subtitle'], 'autore': m['authorPseudonym'],
        'instagram': m['instagramUrl'], 'handle': m['instagramHandle'], 'opera': m['originalWork'],
        'prefazione': m.get('preface'), 'notaAutore': m.get('authorNote'),
        'moods': [x for x in m['macroMoods'] if x['key'] != 'all'] + ([{'key': 'nuovi', 'name': 'I Versi Nuovi', 'desc': 'Le poesie nate dopo il libro e pubblicate su Instagram: ancora senza stanza, ancora calde.', 'color': '#8fa6a0'}] if nuove else []), 'temi': THEME_LABEL}
json.dump({'meta': meta, 'poems': poems}, open(f'{ROOT}/src/data/poems.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(poems), 'poesie;', Counter(t for p in poems for t in p['temi']))
