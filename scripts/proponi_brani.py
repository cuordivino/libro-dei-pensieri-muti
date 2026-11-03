# -*- coding: utf-8 -*-
"""Propone un brano per ogni poesia che ne e' priva, partendo dal TESTO della poesia (temi, immagini, lessico).
Uso: python3 scripts/proponi_brani.py   poi  npm run data.  Scrive src/data/brani-proposti.json (non tocca musica.csv ne' i brani gia' scelti). Sono PROPOSTE: ascoltale e conferma o cambia
scrivendo il brano in scripts/musica.csv (ha la precedenza)."""
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
POOL += [l.split('|') for l in '''Ludovico Einaudi|Time Lapse|tempo memoria quiete
Ludovico Einaudi|Underwater|mare silenzio quiete
Ludovico Einaudi|Run|rinascita rabbia
Ludovico Einaudi|Orbit|tempo notte
Ludovico Einaudi|Lady Labyrinth|notte attesa
Max Richter|Infra 5|perdita silenzio abisso
Max Richter|Shadow Journal|notte assenza
Nils Frahm|More|tempo attesa rinascita
Nils Frahm|Over There, It's Raining|mare silenzio
Ólafur Arnalds|So Close|amore assenza
Ólafur Arnalds|Ekki Hugsa|perdita notte
Jóhann Jóhannsson|The Sun's Gone Dim and the Sky's Turned Black|abisso sacro perdita
Hans Zimmer|Mountains|tempo attesa
Hans Zimmer|S.T.A.Y.|amore tempo memoria
Hans Zimmer|Dream Is Collapsing|abisso rabbia
Hildur Guðnadóttir|Bathroom Dance|maschera carne
Ryuichi Sakamoto|Merry Christmas Mr. Lawrence|memoria amore perdita
Ryuichi Sakamoto|Energy Flow|quiete silenzio
Joe Hisaishi|One Summer's Day|memoria rinascita
Yiruma|Kiss the Rain|amore memoria
Erik Satie|Gymnopédie No. 2|quiete memoria
Frédéric Chopin|Prelude in E minor, Op. 28 No. 4|perdita abisso
Claude Debussy|Arabesque No. 1|rinascita quiete
Sergei Rachmaninoff|Piano Concerto No. 2 (Adagio sostenuto)|amore perdita attesa
Johann Sebastian Bach|Cello Suite No. 1: Prélude|tempo quiete
Johann Sebastian Bach|Jesu, Joy of Man's Desiring|sacro rinascita
Antonio Vivaldi|Winter: Largo|quiete tempo
Georg Friedrich Händel|Sarabande|perdita sacro
Johann Pachelbel|Canon in D|amore tempo
Wolfgang Amadeus Mozart|Piano Concerto No. 21: Andante|amore quiete
Ludwig van Beethoven|Symphony No. 7: Allegretto|perdita tempo
Franz Schubert|Impromptu No. 3 in G-flat major|quiete memoria
Franz Liszt|Liebestraum No. 3|amore carne
Giuseppe Verdi|Va, pensiero|sacro perdita rabbia
Giacomo Puccini|Nessun dorma|rinascita attesa
Giacomo Puccini|O mio babbino caro|amore
Fabrizio De André|Khorakhanè (A forza di essere vento)|perdita rabbia
Fabrizio De André|Via del Campo|carne amore maschera
Fabrizio De André|Amico fragile|assenza maschera abisso
Fabrizio De André|Un giudice|maschera rabbia
Fabrizio De André|Dolcenera|mare rabbia perdita
Fabrizio De André|La guerra di Piero|rabbia perdita
Fabrizio De André|Il testamento di Tito|sacro maschera rabbia
Fabrizio De André|Ave Maria|sacro amore quiete
Franco Battiato|Centro di gravità permanente|maschera tempo
Franco Battiato|E ti vengo a cercare|amore sacro attesa
Franco Battiato|L'era del cinghiale bianco|tempo memoria
Franco Battiato|Gli uccelli|rinascita silenzio
Franco Battiato|Shackleton|abisso attesa
Lucio Dalla|Caruso|amore perdita
Lucio Dalla|L'anno che verrà|attesa rinascita
Giorgio Gaber|Il conformista|maschera
Luigi Tenco|Ciao amore ciao|perdita
Mia Martini|Minuetto|carne perdita
Mina|Il cielo in una stanza|amore
Paolo Conte|Azzurro|attesa memoria
Paolo Conte|Sparring Partner|maschera carne notte
Vinicio Capossela|Il pumo|sacro maschera
Afterhours|Hai paura del buio?|notte abisso rabbia
Massimo Volume|Il primo dio|sacro abisso
Carmen Consoli|Parole di burro|rabbia maschera
Elisa|Luce (Tramonti a nord est)|rinascita
Leonard Cohen|Suzanne|amore sacro mare
Leonard Cohen|So Long, Marianne|perdita amore
Leonard Cohen|Dance Me to the End of Love|amore carne
Leonard Cohen|Bird on the Wire|perdita rabbia
Leonard Cohen|Who by Fire|sacro tempo
Nick Cave & The Bad Seeds|The Mercy Seat|sacro rabbia abisso
Nick Cave & The Bad Seeds|Where the Wild Roses Grow|carne amore abisso
Nick Cave & The Bad Seeds|Brompton Oratory|sacro carne
Nick Cave & The Bad Seeds|Straight to You|amore attesa
PJ Harvey|To Bring You My Love|carne sacro
Tom Waits|Jersey Girl|amore carne
Tom Waits|Downtown Train|attesa notte
Nina Simone|Sinnerman|sacro rabbia
Nina Simone|I Put a Spell on You|carne rabbia
Nina Simone|Don't Let Me Be Misunderstood|maschera perdita
Édith Piaf|Non, je ne regrette rien|rinascita memoria
Jacques Brel|Ne me quitte pas|amore perdita attesa
Léo Ferré|Avec le temps|tempo perdita memoria
Barbara|Göttingen|memoria quiete
Pink Floyd|Comfortably Numb|assenza abisso
Pink Floyd|Wish You Were Here|assenza memoria
Pink Floyd|Echoes|mare abisso tempo
Led Zeppelin|Stairway to Heaven|sacro rinascita
The Doors|The End|abisso rabbia carne
The Doors|Riders on the Storm|notte mare
The Velvet Underground|Venus in Furs|carne maschera
The Velvet Underground|Sunday Morning|attesa quiete
David Bowie|Space Oddity|assenza silenzio
David Bowie|Heroes|rinascita amore
The Cure|Lullaby|notte abisso
The Cure|Disintegration|perdita abisso
Bauhaus|Bela Lugosi's Dead|notte abisso maschera
The Smiths|How Soon Is Now?|assenza maschera
Cocteau Twins|Heaven or Las Vegas|rinascita amore
This Mortal Coil|Song to the Siren|mare amore perdita
Slowdive|When the Sun Hits|rinascita notte
Mogwai|Take Me Somewhere Nice|quiete attesa
Björk|Hyperballad|abisso amore
Radiohead|Street Spirit (Fade Out)|abisso perdita
Radiohead|Exit Music (For a Film)|perdita notte
Portishead|Wandering Star|assenza abisso
Massive Attack|Unfinished Sympathy|amore attesa
Mazzy Star|Into Dust|perdita quiete
Antony and the Johnsons|Hope There's Someone|assenza notte abisso
Hozier|Work Song|amore perdita sacro
Florence + The Machine|Dog Days Are Over|rinascita
Bon Iver|Holocene|memoria quiete
Bon Iver|re: Stacks|perdita quiete
Fleet Foxes|White Winter Hymnal|silenzio memoria
Nick Drake|Fruit Tree|perdita memoria
Sinéad O'Connor|Nothing Compares 2 U|assenza perdita
Fiona Apple|Criminal|maschera rabbia carne
Tori Amos|Winter|memoria perdita
Kate Bush|Wuthering Heights|amore abisso
Kate Bush|This Woman's Work|perdita amore
Peter Gabriel|Mercy Street|sacro perdita notte
Peter Gabriel|Here Comes the Flood|mare rabbia
Annie Lennox|Why|perdita rabbia
Bill Evans|Waltz for Debby|amore quiete
John Coltrane|Naima|amore quiete
Keith Jarrett|The Köln Concert, Part I|tempo rinascita
Thelonious Monk|'Round Midnight|notte attesa
Chet Baker|Almost Blue|perdita notte'''.split('\n')]
norm = lambda s: re.sub(r'[^a-z0-9]+', '', unicodedata.normalize('NFD', s.lower()).encode('ascii', 'ignore').decode())
mp = f'{HERE}/musica.csv'; rows = list(csv.DictReader(open(mp, encoding='utf-8')))
pj = f'{ROOT}/src/data/brani-proposti.json'; old = json.load(open(pj, encoding='utf-8')) if os.path.exists(pj) else {}
used = {norm(r['brano']) for r in rows if r['brano'].strip()} | {norm(p['musica']['brano']) for p in P if p['musica']['brano']} | {norm(v['brano']) for v in old.values()}
need = [p for p in P if not p['musica']['brano'].strip() and str(p['id']) not in old]
def tags(p):
    t = (p['titolo'] + ' ' + p['testo']).lower()
    return {k: min(3, len(re.findall(rx, t))) for k, rx in LEX.items() if re.search(rx, t)}
cand = []
for p in need:
    pt = tags(p) or {'silenzio': 1, 'quiete': 1, 'tempo': 1}
    for a, b, tg in POOL:
        if norm(b) in used: continue
        m = [x for x in tg.split() if x in pt]
        sc = sum(pt[x] for x in m) + 0.01 * (int(hashlib.md5((str(p['id']) + b).encode()).hexdigest(), 16) % 100) / 100
        if m: cand.append((sc, str(p['id']), a, b, m))
cand.sort(reverse=True); done = dict(old); taken = set()
for sc, pid, a, b, m in cand:
    if pid in done or norm(b) in taken: continue
    done[pid] = {'artista': a, 'brano': b, 'perche': 'Proposta dal testo: richiama ' + ', '.join(m) + '.'}; taken.add(norm(b))
json.dump(done, open(pj, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'proposti {len(done) - len(old)} brani su {len(need)} poesie senza brano; senza proposta: {[p["id"] for p in need if str(p["id"]) not in done]}')
