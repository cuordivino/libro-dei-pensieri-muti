# -*- coding: utf-8 -*-
"""Propone un brano per ogni poesia che ne e' priva, partendo dal TESTO della poesia (temi, immagini, lessico).
Uso: python3 scripts/proponi_brani.py   poi  npm run data.  Scrive solo le righe vuote di scripts/musica.csv:
brano, artista e `perche` (motivo). Sono PROPOSTE: ascoltale e conferma o cambia. Non tocca i brani gia' scelti."""
import os, re, csv, json, hashlib, unicodedata
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
P = json.load(open(f'{ROOT}/src/data/poems.json', encoding='utf-8'))['poems']
LEX = {
 'sacro': r'\bdio\b|\bdei\b|\bpreghier|\bchies|\bsant[oi]\b|\bcroce|\baltare|\btonaca|\bbestemm|\bangel|\bdemon|\bparadis|\binferno|\bsacr|\bfede\b|\bmessa\b|\bcielo|\bsalmo|\bcristo|\bsignore|\bgrazia',
 'carne': r'\bcarn|\bcorpo|\bcorpi|\bbaci|\blabbra|\bpelle|\bdesider|\bbram|\blussur|\bnud|\bsudor|\bsangue|\bseno\b|\bmani\b|\bfianch|\bgola',
 'rabbia': r'\brabbia|\burlo|\bfuria|\bgrid|\bferro|\bspada|\bfuoco|\bguerra|\bodio|\bribell|\bfrusta|\bbrucia|\bvendetta',
 'abisso': r'\babiss|\bpozzo|\bfondo|\bbuio|\boscur|\bnero\b|\bvuot|\bbaratro|\bprecipit|\bcade\b|\bcadut|\bombra',
 'maschera': r'\bmaschera|\bfint|\bvolto|\bipocri|\bfango|\bbugi|\bmenzogn|\bteatr|\bclown|\bgioco|\bcommedia',
 'quiete': r'\bquiet|\bpace\b|\bcalm|\bdolce|\blieve|\bcarezz|\btenerezz|\bnido|\bpiano\b|\bserena',
 'mare': r'\bmare\b|\bond[ae]\b|\bacqua|\briva\b|\bnaufrag|\bmarin|\bvela\b|\bpioggia|\bannego|\baffog',
 'notte': r'\bnott|\bluna\b|\bstell|\btenebr|\bnebbia|\bbuio|\bsogn',
 'perdita': r'\bperdu|\bperd[oe]|\blutto|\bmort|\baddio|\bsvanis|\bcade\b|\blacrim|\bpiang|\bdolore|\bferita',
 'memoria': r'\bricord|\bmemori|\bpassat|\bieri\b|\bnostalg|\binfanzia',
 'attesa': r'\battend|\battes|\baspett|\bsperan|\bancora\b|\bresto\b',
 'rinascita': r'\brinasc|\briaffior|\brisorg|\balba\b|\bgermogl|\britrov|\bluce\b|\blevigh|\bvola|\bali\b',
 'tempo': r'\btemp[oi]\b|\battim|\banni\b|\bsera\b|\beterno|\bistante|\bclessidra|\borologio',
 'silenzio': r'\bsilenz|\bmut[oai]\b|\btaci|\bzitt',
 'assenza': r'\bassenz|\bniente|\bnulla\b|\bmanc|\blontan',
 'amore': r'\bamor|\bcuore|\babbracc|\bamat',
}
# (artista, brano, tag)  — tutti brani reali e ben noti
POOL = [l.split('|') for l in '''Hozier|Take Me to Church|sacro carne rabbia amore
Depeche Mode|Personal Jesus|sacro carne maschera
Depeche Mode|Enjoy the Silence|silenzio amore
Leonard Cohen|Hallelujah|sacro amore perdita
Leonard Cohen|Famous Blue Raincoat|perdita memoria assenza
Leonard Cohen|Avalanche|abisso rabbia notte
Nick Cave & The Bad Seeds|Into My Arms|sacro amore perdita
Nick Cave & The Bad Seeds|Red Right Hand|notte abisso maschera
Johnny Cash|Hurt|perdita memoria tempo
Jeff Buckley|Lover, You Should've Come Over|amore perdita attesa
Jeff Buckley|Grace|perdita abisso amore
Radiohead|Motion Picture Soundtrack|sacro perdita quiete
Radiohead|How to Disappear Completely|assenza abisso silenzio
Radiohead|Pyramid Song|tempo mare abisso
Portishead|Roads|perdita abisso notte
Portishead|Glory Box|carne amore maschera
Massive Attack|Teardrop|amore tempo notte
Massive Attack|Angel|carne abisso rabbia
Mazzy Star|Fade Into You|amore attesa notte
Joy Division|Atmosphere|perdita abisso silenzio
Joy Division|Love Will Tear Us Apart|amore rabbia perdita
The Cure|Pictures of You|memoria perdita amore
The Cure|A Forest|notte abisso attesa
Nine Inch Nails|Something I Can Never Have|perdita rabbia notte
Tom Waits|Tom Traubert's Blues|perdita maschera notte memoria
Tom Waits|Hope I Don't Fall in Love with You|amore attesa notte
Nina Simone|Wild Is the Wind|amore attesa carne
Nina Simone|Feeling Good|rinascita
Chet Baker|I Fall in Love Too Easily|amore perdita notte
Fabrizio De André|Hotel Supramonte|perdita notte silenzio memoria
Fabrizio De André|Preghiera in gennaio|sacro perdita
Fabrizio De André|Il pescatore|mare quiete
Fabrizio De André|La canzone di Marinella|mare perdita amore
Fabrizio De André|Bocca di rosa|carne maschera
Franco Battiato|La cura|amore rinascita sacro
Franco Battiato|Prospettiva Nevski|tempo memoria notte
Franco Battiato|Povera patria|rabbia maschera
Luigi Tenco|Vedrai, vedrai|attesa amore rinascita
Luigi Tenco|Mi sono innamorato di te|amore perdita
Lucio Battisti|Ancora tu|amore rabbia attesa
Mina|Se telefonando|amore perdita
Ludovico Einaudi|I Giorni|memoria tempo quiete
Ludovico Einaudi|Primavera|rinascita
Ludovico Einaudi|Le Onde|mare quiete
Ludovico Einaudi|Fuori dal mondo|assenza silenzio
Ludovico Einaudi|Eros|carne amore
Ludovico Einaudi|Nightbook|notte
Ludovico Einaudi|Life|tempo memoria
Max Richter|Vladimir's Blues|silenzio assenza
Max Richter|Sarajevo|perdita sacro
Max Richter|Dream 3 (in the midst of my life)|notte quiete tempo
Max Richter|Path 5 (delta)|memoria quiete
Nils Frahm|Ambre|quiete memoria
Nils Frahm|Spells|attesa tempo
Nils Frahm|Hammers|rabbia carne
Arvo Pärt|Fratres|sacro tempo
Arvo Pärt|Für Alina|silenzio quiete
Arvo Pärt|Cantus in Memoriam Benjamin Britten|perdita sacro memoria
Erik Satie|Gnossienne No. 1|notte attesa maschera
Erik Satie|Gymnopédie No. 3|quiete memoria
Claude Debussy|Clair de Lune|notte amore quiete
Claude Debussy|Rêverie|quiete memoria
Frédéric Chopin|Nocturne in E-flat major, Op. 9 No. 2|notte amore memoria
Ludwig van Beethoven|Moonlight Sonata (1st movement)|notte perdita
Johann Sebastian Bach|Air on the G String|sacro quiete
Johann Sebastian Bach|Aria (Goldberg Variations)|quiete tempo
Johann Sebastian Bach|Chaconne (Partita No. 2)|abisso sacro perdita
Wolfgang Amadeus Mozart|Lacrimosa|sacro perdita
Gregorio Allegri|Miserere|sacro perdita
Giovanni Battista Pergolesi|Stabat Mater|sacro perdita
Samuel Barber|Adagio for Strings|perdita sacro
Tomaso Albinoni|Adagio in G minor|perdita
Henryk Górecki|Symphony No. 3 (Lento - Sostenuto tranquillo ma cantabile)|perdita abisso sacro
Gabriel Fauré|Requiem: In Paradisum|sacro quiete rinascita
Maurice Ravel|Pavane pour une infante défunte|memoria perdita
Gustav Mahler|Symphony No. 5: Adagietto|amore perdita
Sergei Rachmaninoff|Vocalise|perdita notte
Franz Schubert|Ave Maria|sacro quiete
Henry Purcell|Dido's Lament (When I Am Laid in Earth)|perdita sacro
Dead Can Dance|The Host of Seraphim|sacro abisso
Sigur Rós|Hoppípolla|rinascita
Sigur Rós|Sæglópur|mare perdita
Explosions in the Sky|Your Hand in Mine|amore rinascita
Jóhann Jóhannsson|Flight from the City|perdita silenzio
Clint Mansell|Lux Aeterna|abisso rabbia sacro
Hans Zimmer|Cornfield Chase|rinascita attesa tempo
Hans Zimmer|Day One|tempo memoria
Ennio Morricone|Gabriel's Oboe|sacro quiete
Astor Piazzolla|Oblivion|perdita carne notte memoria
Astor Piazzolla|Libertango|carne rabbia
Agnes Obel|Familiar|attesa notte
Agnes Obel|Fuel to Fire|perdita silenzio
Yann Tiersen|Porz Goret|mare memoria quiete
Angelo Badalamenti|Laura Palmer's Theme|notte carne perdita
Bohren & der Club of Gore|Sunset Mission|notte carne abisso
Brian Eno|Music for Airports 1/1|quiete silenzio tempo
Bon Iver|Skinny Love|perdita amore
Damien Rice|The Blower's Daughter|amore perdita attesa
Elliott Smith|Between the Bars|abisso amore
Nick Drake|Pink Moon|notte mare memoria
Nick Drake|River Man|mare tempo
Cigarettes After Sex|Nothing's Gonna Hurt You Baby|amore carne attesa
Beach House|Space Song|notte amore
Ólafur Arnalds|Reminiscence|memoria quiete
Hania Rani|Esja|quiete memoria
Dustin O'Halloran|Opus 23|perdita quiete
Michael Nyman|The Heart Asks Pleasure First|amore carne
Philip Glass|Metamorphosis Two|tempo memoria
Philip Glass|Opening|tempo quiete
Gustavo Santaolalla|Iguazu|quiete memoria
Bill Evans|Peace Piece|quiete
Miles Davis|Blue in Green|notte perdita attesa'''.split('\n')]
norm = lambda s: re.sub(r'[^a-z0-9]+', '', unicodedata.normalize('NFD', s.lower()).encode('ascii', 'ignore').decode())
mp = f'{HERE}/musica.csv'; rows = list(csv.DictReader(open(mp, encoding='utf-8')))
used = {norm(r['brano']) for r in rows if r['brano'].strip()}
need = [r for r in rows if not r['brano'].strip()]
poem = {str(p['id']): p for p in P}
def tags(p):
    t = (p['titolo'] + ' ' + p['testo']).lower()
    return {k: min(3, len(re.findall(rx, t))) for k, rx in LEX.items() if re.search(rx, t)}
cand = []
for r in need:
    pt = tags(poem[r['id']])
    for a, b, tg in POOL:
        if norm(b) in used: continue
        m = [x for x in tg.split() if x in pt]
        sc = sum(pt[x] for x in m) + 0.01 * (int(hashlib.md5((r['id'] + b).encode()).hexdigest(), 16) % 100) / 100
        if m: cand.append((sc, r['id'], a, b, m))
cand.sort(reverse=True); done = {}; taken = set()
for sc, pid, a, b, m in cand:
    if pid in done or norm(b) in taken: continue
    done[pid] = (a, b, m); taken.add(norm(b))
import urllib.parse as up
for r in need:
    if r['id'] in done:
        a, b, m = done[r['id']]
        r['brano'], r['artista'] = b, a
        r['perche'] = 'Proposta dal testo: richiama ' + ', '.join(m) + '.'
        r['cerca_youtube'] = 'https://www.youtube.com/results?search_query=' + up.quote(f'{b} {a}')
w = csv.DictWriter(open(mp, 'w', encoding='utf-8', newline=''), rows[0].keys()); w.writeheader(); w.writerows(rows)
print(f'proposti {len(done)} brani su {len(need)} poesie senza brano; senza proposta: {[r["id"] for r in need if r["id"] not in done]}')
