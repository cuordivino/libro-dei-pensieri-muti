import raw from '../data/poems.json';

export type Poem = (typeof raw.poems)[number];
export const meta = raw.meta;
export const poems: Poem[] = raw.poems;
export const base = import.meta.env.BASE_URL.replace(/\/$/, '');
export const u = (p = '') => `${base}/${p.replace(/^\//, '')}`;
export const byId = (id: number) => poems.find((p) => p.id === id)!;
export const lines = (t: string) => t.split('\n');
export const stanzas = (t: string) => t.trim().split(/\n\s*\n/).map((s) => s.split('\n'));
export const SITE = 'https://cuordivino.github.io';

export const THEME_INTRO: Record<string, string> = {
  memoria: 'Ciò che resta quando il giorno è passato: immagini, voci, un filo che non si spezza.',
  amore: 'Desiderio, corpo, tenerezza e vertigine: l’amore nei suoi gesti più nudi.',
  perdita: 'Ciò che cade, svanisce, non torna. Versi per attraversare l’addio.',
  silenzio: 'Il non detto che pesa e cura. Il silenzio come stanza e come ferita.',
  assenza: 'Il vuoto che ha una forma precisa, e un nome che non si pronuncia.',
  tempo: 'L’attimo esatto, il giorno che scorre, l’eternità che si incrina.',
  mare: 'Acqua, profondità, naufragio e riva: immergersi per poi riaffiorare.',
  notte: 'Ombra, nebbia e luna: ciò che si vede solo quando la luce si ritira.',
  attesa: 'Restare, sperare, aspettare ancora. Il tempo sospeso prima di un ritorno.',
  rinascita: 'Il verso che germoglia dal fondo, la luce che riaffiora dopo l’abisso.',
};

export const themeCounts = Object.keys(meta.temi)
  .map((t) => ({ key: t, label: (meta.temi as Record<string, string>)[t], n: poems.filter((p) => p.temi.includes(t)).length }))
  .filter((t) => t.n >= 3);

import config from '../data/config.json';
export { config };
/** Indirizzo del lettore incorporato, solo se il brano ha un link diretto. */
export function embedUrl(m: Record<string, any>) {
  const sp = /open\.spotify\.com\/(?:intl-[a-z]+\/)?track\/([A-Za-z0-9]+)/.exec(m.spotify ?? '');
  if (sp) return { kind: 'Spotify', url: `https://open.spotify.com/embed/track/${sp[1]}`, h: 152 };
  const yt = /(?:v=|youtu\.be\/)([A-Za-z0-9_-]{11})/.exec(m.youtube ?? '');
  if (yt) return { kind: 'YouTube', url: `https://www.youtube-nocookie.com/embed/${yt[1]}`, h: 200 };
  return null;
}

/** ID del video YouTube, se il brano ha un indirizzo diretto. */
export const ytId = (m: Record<string, any>) => /(?:v=|youtu\.be\/)([A-Za-z0-9_-]{11})/.exec(m.youtube ?? '')?.[1] ?? null;
