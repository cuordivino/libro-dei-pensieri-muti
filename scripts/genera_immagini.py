# -*- coding: utf-8 -*-
"""Crea immagini astratte in bianco e nero (chiaroscuro, grana) per le poesie che non hanno un'immagine del profilo.
Non sono fotografie: sono texture generate dal testo/tema di ciascuna poesia. Per sostituirne una con una foto vera basta
salvare public/images/gen/NNN.jpg (1200x1500) e NNN-800.webp (800x1000) con lo stesso nome.
Uso:  python3 scripts/genera_immagini.py            (tutte le poesie senza immagine di Instagram)
      python3 scripts/genera_immagini.py --prova    (una per tipo, in /tmp/prova.png)"""
import os, sys, json, math, hashlib, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
W, H = 600, 750
def rng(seed): return np.random.default_rng(int(hashlib.md5(str(seed).encode()).hexdigest()[:8], 16))
_FX = np.fft.rfftfreq(W)[None, :]; _FY = np.fft.fftfreq(H)[:, None]
def blur(a, sigma):
    k = np.exp(-2 * (np.pi * sigma) ** 2 * (_FX ** 2 + _FY ** 2)); return np.fft.irfft2(np.fft.rfft2(a) * k, s=a.shape)
def noise(r, f):
    sigma = max(1.0, W / (f * 1.6)); a = blur(r.standard_normal((H, W)).astype('float32'), sigma)
    a = (a - a.mean()) / (a.std() + 1e-6); return np.clip(.5 + a * .22, 0, 1).astype('float32')
def fbm(r, base=3, octv=5):
    out = np.zeros((H, W), 'float32'); a = 1.0; tot = 0
    for i in range(octv): out += a * (noise(r, base * 2 ** i) - .5); tot += a; a *= 0.55
    out = out / tot; out = (out - out.mean()) / (out.std() + 1e-6); return np.clip(.5 + out * .2, 0, 1).astype('float32')
def warp(img, r, amt=40, base=2):
    dx = (fbm(r, base, 3) - .5) * amt; dy = (fbm(r, base, 3) - .5) * amt
    yy, xx = np.mgrid[0:H, 0:W]; xs = np.clip((xx + dx).astype(int), 0, W - 1); ys = np.clip((yy + dy).astype(int), 0, H - 1)
    return img[ys, xs]
sm = lambda x, a, b: np.clip((x - a) / (b - a + 1e-6), 0, 1) ** 2 * (3 - 2 * np.clip((x - a) / (b - a + 1e-6), 0, 1))
yy, xx = np.mgrid[0:H, 0:W].astype('float32'); X = xx / W; Y = yy / H
def fumo(r):
    f = fbm(r, 2, 6); f = warp(f, r, 90, 2); f = warp(f, r, 50, 3)
    cx, cy = r.uniform(.3, .7), r.uniform(.25, .6); d = np.hypot(X - cx, (Y - cy) * 1.25)
    return (sm(f, .3, .85) ** 1.4) * (1 - sm(d, .05, .85)) ** .8 * 1.25 + .015
def luce(r):
    ang = r.uniform(.5, 1.0); u = X * math.cos(ang) + Y * math.sin(ang)
    sh = np.zeros((H, W), 'float32')
    for i in range(r.integers(3, 6)):
        c = r.uniform(0, 1.2); w = r.uniform(.03, .1); sh += np.exp(-((u - c) / w) ** 2) * r.uniform(.5, 1)
    sx, sy = r.uniform(0, .3), r.uniform(0, .2); fall = np.exp(-np.hypot(X - sx, Y - sy) * 1.6)
    dust = sm(fbm(r, 14, 3), .55, .9) * .5
    return np.clip(sh * fall * .9 + dust * fall + .02, 0, 1)
def acqua(r):
    hor = r.uniform(.42, .6); sky = (1 - Y) * .55 * sm(fbm(r, 2, 4), .2, .9) + .1
    pers = np.maximum(Y - hor, 0.002); rip = .5 + .5 * np.sin(.9 / pers * .08 + (fbm(r, 5, 3) - .5) * 9)
    sx = r.uniform(.35, .65); refl = np.exp(-((X - sx) / (.03 + pers * .5)) ** 2) * sm(Y, hor, hor + .4)
    water = (rip * .35 + refl * 1.2) * sm(Y, hor, hor + .05) * (1 - (Y - hor) * 1.1)
    out = np.where(Y < hor, sky, water); out = out + np.exp(-((Y - hor) / .004) ** 2) * .5
    return np.clip(out, 0, 1)
def pozzo(r):
    cx, cy = r.uniform(.42, .58), r.uniform(.38, .55); d = np.hypot((X - cx) * 1.0, (Y - cy) * .8) + 1e-3
    d = np.maximum(d + (fbm(r, 4, 3) - .5) * .08, 1e-3)
    rings = .5 + .5 * np.sin(np.log(d) * r.uniform(7, 12) + r.uniform(0, 6)); core = np.exp(-d * r.uniform(5, 9))
    haze = sm(fbm(r, 3, 4), .35, .85) * .35
    return np.clip(rings * sm(d, .05, .6) * (1 - sm(d, .5, 1.0)) * .16 + haze * (1 - sm(d, .2, 1.0)) + core * 1.15 + .012, 0, 1)
def tessitura(r):
    h = warp(fbm(r, 2, 5), r, 120, 2) * 6 + np.sin(Y * r.uniform(5, 11) + fbm(r, 2, 3) * 8) * .6
    gy, gx = np.gradient(h); lx, ly = -.6, -.7; sh = (gx * lx + gy * ly) * 2.2
    out = sm(.5 + sh, .25, .9) * (.35 + .65 * sm(np.hypot(X - .5, Y - .45), 1.0, .1))
    return np.clip(out, 0, 1)
def tratto(r):
    img = Image.new('L', (W, H), 0); d = ImageDraw.Draw(img)
    for i in range(r.integers(5, 10)):
        x0, y0 = r.uniform(0, W), r.uniform(0, H); x1, y1 = x0 + r.uniform(-W, W) * .8, y0 + r.uniform(-H, H) * .6
        cx, cy = (x0 + x1) / 2 + r.uniform(-150, 150), (y0 + y1) / 2 + r.uniform(-150, 150); wd = r.uniform(8, 46)
        pts = [((1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t * t * x1, (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t * t * y1) for t in np.linspace(0, 1, 40)]
        for k, (px, py) in enumerate(pts):
            w = wd * (1 - abs(k / 39 - .45) * 1.2); d.ellipse([px - w, py - w, px + w, py + w], fill=255)
    a = np.asarray(img.filter(ImageFilter.GaussianBlur(2.2)), dtype='float32') / 255
    tex = fbm(r, 10, 4); a = np.clip(a * (.5 + tex), 0, 1); a = a * sm(fbm(r, 3, 3), .2, .7)
    return 1 - a * .92 if r.random() < .5 else a
MOT = {'fumo': fumo, 'luce': luce, 'acqua': acqua, 'pozzo': pozzo, 'tessitura': tessitura, 'tratto': tratto}
TEMA = {'mare': ['fumo', 'pozzo'], 'abisso': ['pozzo'], 'perdita': ['fumo', 'pozzo'], 'silenzio': ['luce', 'fumo'], 'notte': ['luce', 'fumo'], 'assenza': ['pozzo', 'luce'],
        'attesa': ['luce', 'fumo'], 'amore': ['tessitura'], 'memoria': ['fumo'], 'tempo': ['fumo', 'pozzo'], 'rinascita': ['luce'], 'rabbia': ['tessitura', 'luce'], 'maschera': ['tessitura', 'fumo']}
def render(pid, temi, seme):
    r = rng(f'{pid}-{seme}'); t = temi[0] if temi else 'silenzio'; mot = TEMA.get(t, ['fumo'])[int(r.integers(0, len(TEMA.get(t, ['fumo']))))]
    a = MOT[mot](r); a = np.clip(a, 0, 1)
    vig = 1 - sm(np.hypot(X - .5, (Y - .5) * .85), .45, .95) * .75; a = a * vig
    lo, hi = np.percentile(a, 2), np.percentile(a, 99.5); a = np.clip((a - lo) / (hi - lo + 1e-6), 0, 1) ** 1.15
    im = Image.fromarray((a * 255).astype('uint8')).resize((1200, 1500), Image.BICUBIC)
    g = rng(f'g{pid}').normal(0, 11, (1500, 1200)).astype('float32'); arr = np.clip(np.asarray(im, dtype='float32') + g * (.35 + .65 * (np.asarray(im) / 255 < .75)), 0, 255)
    return Image.fromarray(arr.astype('uint8')).convert('RGB'), mot
if '--prova' in sys.argv:
    sheet = Image.new('RGB', (6 * 300, 375), '#333')
    for i, (m, t) in enumerate([('fumo', ['perdita']), ('luce', ['notte']), ('acqua', ['mare']), ('pozzo', ['abisso']), ('tessitura', ['amore']), ('tratto', ['rabbia'])]):
        im, mot = render(100 + i, t, 'prova'); sheet.paste(im.resize((300, 375)), (i * 300, 0))
    sheet.save('/tmp/prova.png'); print('prova scritta'); sys.exit()
P = json.load(open(f'{ROOT}/src/data/poems.json', encoding='utf-8'))['poems']
os.makedirs(f'{ROOT}/public/images/gen', exist_ok=True); n = 0
for p in P:
    if str(p['immagine']).startswith('ig/'): continue
    im, mot = render(p['id'], p['temi'], 'v1'); im.save(f"{ROOT}/public/images/gen/{p['id']}.jpg", quality=80, optimize=True, progressive=True)
    s = im.copy(); s.thumbnail((800, 1000)); s.save(f"{ROOT}/public/images/gen/{p['id']}-800.webp", quality=72); n += 1
print(n, 'immagini generate')
