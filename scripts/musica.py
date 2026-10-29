# -*- coding: utf-8 -*-
"""Gestione dei brani. `python3 scripts/musica.py` crea/aggiorna scripts/musica.csv con un brano per poesia.
Compila le colonne spotify / youtube con l'indirizzo DIRETTO del brano (per attivare il lettore integrato),
scrivi in `perche` il legame con la poesia e metti `si` in `verificato` quando hai controllato la coerenza.
Poi:  npm run data"""
import json, csv, os
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
poems = json.load(open(f'{ROOT}/src/data/poems.json', encoding='utf-8'))['poems']
p = f'{HERE}/musica.csv'
old = {r['id']: r for r in csv.DictReader(open(p, encoding='utf-8'))} if os.path.exists(p) else {}
cols = ['id', 'titolo', 'stato_animo', 'brano', 'artista', 'spotify', 'youtube', 'apple', 'soundcloud', 'perche', 'verificato']
with open(p, 'w', encoding='utf-8', newline='') as f:
    w = csv.DictWriter(f, cols); w.writeheader()
    for x in poems:
        o = old.get(str(x['id']), {})
        w.writerow({'id': x['id'], 'titolo': x['titolo'], 'stato_animo': x['moodNome'],
                    'brano': o.get('brano') or x['musica']['brano'], 'artista': o.get('artista') or x['musica']['artista'],
                    **{k: o.get(k, '') for k in ('spotify', 'youtube', 'apple', 'soundcloud', 'perche', 'verificato')}})
print('scritto', p, '—', len(poems), 'righe')
