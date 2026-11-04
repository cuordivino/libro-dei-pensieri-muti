// Servizio commenti per Il Libro dei Pensieri Muti — Cloudflare Worker + D1.
const J = (o, s = 200, h = {}) => new Response(JSON.stringify(o), { status: s, headers: { 'content-type': 'application/json', ...h } });
const cors = (env) => ({ 'access-control-allow-origin': env.SITE_ORIGIN, 'access-control-allow-headers': 'content-type, authorization', 'access-control-allow-methods': 'GET, POST, OPTIONS', vary: 'origin' });
const clean = (s, n) => String(s ?? '').replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F]/g, '').replace(/<[^>]*>/g, '').trim().slice(0, n);
const sha = async (t) => [...new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(t)))].map((b) => b.toString(16).padStart(2, '0')).join('');
const same = (a, b) => { if (a.length !== b.length) return false; let r = 0; for (let i = 0; i < a.length; i++) r |= a.charCodeAt(i) ^ b.charCodeAt(i); return r === 0; };


const day = () => new Date().toISOString().slice(0, 10);
const BOT = /bot|crawl|spider|headless|preview|facebookexternalhit|slurp/i;
const bayes = (avg, n, m) => (n * avg + 3 * m) / (n + 3);
async function ratingOf(env, pid) { const r = await env.DB.prepare('SELECT AVG(value) a, COUNT(*) n FROM votes WHERE poem_id=?').bind(pid).first(); return { avg: r.n ? Math.round(r.a * 10) / 10 : null, n: r.n }; }

async function mail(env, to, subject, text) {
  if (!env.RESEND_API_KEY || !to) return false;
  const r = await fetch('https://api.resend.com/emails', { method: 'POST', headers: { authorization: `Bearer ${env.RESEND_API_KEY}`, 'content-type': 'application/json' }, body: JSON.stringify({ from: env.MAIL_FROM, to, subject, text }) });
  return r.ok;
}
const validContact = (t, c) => t === 'none' || (t === 'email' ? /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(c) : t === 'phone' ? /^\+?[\d\s().-]{7,20}$/.test(c) : c.length >= 2);

export default {
  async fetch(req, env, ctx) {
    const url = new URL(req.url), H = cors(env), path = url.pathname.replace(/\/$/, '');
    if (req.method === 'OPTIONS') return new Response(null, { status: 204, headers: H });
    try {
      // pubblico: commenti approvati e pubblicabili
      if (req.method === 'GET' && path === '/comments') {
        const pid = parseInt(url.searchParams.get('poem'), 10); if (!pid) return J({ error: 'poesia mancante' }, 400, H);
        const { results } = await env.DB.prepare("SELECT name, message, reply, created_at FROM comments WHERE poem_id=? AND status='approved' AND public=1 ORDER BY id DESC LIMIT 100").bind(pid).all();
        return J({ comments: results }, 200, { ...H, 'cache-control': 'public, max-age=60' });
      }
      // pubblico: conteggio visite (anonimo: nessun cookie, nessun IP salvato; solo un'impronta giornaliera non reversibile)
      if (req.method === 'POST' && path === '/view') {
        const b = await req.json().catch(() => ({})), pid = parseInt(b.poem, 10) || 0;
        if (pid < 0 || pid > 100000 || BOT.test(req.headers.get('user-agent') || '')) return new Response(null, { status: 204, headers: H });
        const d = day(), ip = req.headers.get('cf-connecting-ip') || '', ua = req.headers.get('user-agent') || '';
        for (const k of (pid > 0 ? [pid, 0] : [0])) {   // ogni pagina conta anche per il totale del sito (poem_id 0)
          const h = await sha(`${ip}|${ua}|${d}|${env.IP_SALT || 'sale'}|${k}`);
          const ins = await env.DB.prepare('INSERT OR IGNORE INTO seen (day, poem_id, h) VALUES (?,?,?)').bind(d, k, h).run(), u = ins.meta.changes ? 1 : 0;
          await env.DB.prepare('INSERT INTO views (poem_id, day, n, u) VALUES (?,?,1,?) ON CONFLICT(poem_id, day) DO UPDATE SET n = n + 1, u = u + ?').bind(k, d, u, u).run();
        }
        return J({ ok: true }, 200, H);
      }
      // pubblico: voto da 1 a 5 (un voto per lettore e per poesia, modificabile; l'identificativo e' casuale e non personale)
      if (req.method === 'POST' && path === '/vote') {
        const b = await req.json().catch(() => null); if (!b) return J({ error: 'richiesta non valida' }, 400, H);
        const pid = parseInt(b.poem, 10), v = parseInt(b.value, 10), voter = String(b.voter || '');
        if (!(pid > 0) || !(v >= 1 && v <= 5) || !/^[A-Za-z0-9_-]{16,64}$/.test(voter)) return J({ error: 'voto non valido' }, 400, H);
        const hv = await sha(voter + (env.IP_SALT || 'sale'));
        await env.DB.prepare('INSERT INTO votes (poem_id, voter, value, created_at) VALUES (?,?,?,?) ON CONFLICT(poem_id, voter) DO UPDATE SET value = excluded.value, created_at = excluded.created_at').bind(pid, hv, v, new Date().toISOString()).run();
        return J({ ok: true, ...(await ratingOf(env, pid)) }, 200, H);
      }
      if (req.method === 'GET' && path === '/rating') {
        const pid = parseInt(url.searchParams.get('poem'), 10); if (!(pid > 0)) return J({ error: 'poesia mancante' }, 400, H);
        return J(await ratingOf(env, pid), 200, { ...H, 'cache-control': 'public, max-age=30' });
      }
      // pubblico: classifiche (solo dati aggregati)
      if (req.method === 'GET' && path === '/stats/public') {
        const vt = (await env.DB.prepare('SELECT poem_id, AVG(value) a, COUNT(*) n FROM votes GROUP BY poem_id').all()).results;
        const tot = vt.reduce((x, r) => x + r.a * r.n, 0), cnt = vt.reduce((x, r) => x + r.n, 0), m = cnt ? tot / cnt : 3.5;
        const amate = vt.map((r) => ({ poem: r.poem_id, avg: Math.round(r.a * 10) / 10, n: r.n, score: bayes(r.a, r.n, m) })).sort((a, b) => b.score - a.score).slice(0, 15);
        const lette = (await env.DB.prepare('SELECT poem_id poem, SUM(n) views FROM views WHERE poem_id > 0 GROUP BY poem_id ORDER BY views DESC LIMIT 15').all()).results;
        const sito = await env.DB.prepare('SELECT COALESCE(SUM(n),0) visite, COALESCE(SUM(u),0) uniche FROM views WHERE poem_id = 0').first();
        return J({ amate, lette, visite: sito.visite, uniche: sito.uniche, voti: cnt }, 200, { ...H, 'cache-control': 'public, max-age=120' });
      }
      // pubblico: nuovo commento
      if (req.method === 'POST' && path === '/comments') {
        const b = await req.json().catch(() => null); if (!b) return J({ error: 'richiesta non valida' }, 400, H);
        if (b.website) return J({ ok: true }, 200, H); // trappola per i bot
        const name = clean(b.name, 60), message = clean(b.message, 1200);
        const ctype = ['none', 'email', 'phone', 'instagram', 'social'].includes(b.ctype) ? b.ctype : 'none';
        const contact = ctype === 'none' ? '' : clean(b.contact, 120), poem = parseInt(b.poem, 10);
        if (!poem || name.length < 2 || message.length < 3) return J({ error: 'Nome e messaggio sono obbligatori.' }, 400, H);
        if (!b.consent) return J({ error: 'Serve il consenso al trattamento dei dati.' }, 400, H);
        if (!validContact(ctype, contact)) return J({ error: 'Il contatto indicato non sembra valido.' }, 400, H);
        const ip = await sha((req.headers.get('cf-connecting-ip') || '') + (env.IP_SALT || 'sale')), now = new Date().toISOString();
        const recent = await env.DB.prepare('SELECT COUNT(*) n FROM comments WHERE ip_hash=? AND created_at>?').bind(ip, new Date(Date.now() - 3600e3).toISOString()).first();
        if (recent.n >= 5) return J({ error: 'Troppi invii ravvicinati: riprova più tardi.' }, 429, H);
        const r = await env.DB.prepare('INSERT INTO comments (poem_id,poem_title,name,message,contact_type,contact,public,consent_at,created_at,ip_hash) VALUES (?,?,?,?,?,?,?,?,?,?)')
          .bind(poem, clean(b.title, 120), name, message, ctype, contact, b.public ? 1 : 0, now, now, ip).run();
        ctx.waitUntil(mail(env, env.OWNER_EMAIL, `Nuovo commento su «${clean(b.title, 80)}»`, `${name} ha scritto:\n\n${message}\n\nCanale di risposta: ${ctype}${contact ? ' — ' + contact : ''}\n\nModera: ${env.SITE_URL}/admin/`));
        return J({ ok: true, id: r.meta.last_row_id }, 201, H);
      }
      // riservato: moderazione
      if (path.startsWith('/admin')) {
        const t = (req.headers.get('authorization') || '').replace(/^Bearer /, '');
        if (!env.ADMIN_TOKEN || !same(t, env.ADMIN_TOKEN)) return J({ error: 'non autorizzato' }, 401, H);
        if (req.method === 'GET' && path === '/admin/stats') {
          const dd = Math.min(365, Math.max(1, parseInt(url.searchParams.get('days'), 10) || 30)), from = new Date(Date.now() - dd * 864e5).toISOString().slice(0, 10);
          const giorni = (await env.DB.prepare('SELECT day, n, u FROM views WHERE poem_id = 0 AND day >= ? ORDER BY day').bind(from).all()).results;
          const poesie = (await env.DB.prepare('SELECT poem_id, SUM(n) views, SUM(u) uniq FROM views WHERE poem_id > 0 AND day >= ? GROUP BY poem_id').bind(from).all()).results;
          const voti = (await env.DB.prepare('SELECT poem_id, AVG(value) avg, COUNT(*) n FROM votes GROUP BY poem_id').all()).results;
          const totali = await env.DB.prepare('SELECT COALESCE(SUM(n),0) visite, COALESCE(SUM(u),0) uniche FROM views WHERE poem_id = 0').first();
          return J({ giorni, poesie, voti, totali, giorniScelti: dd }, 200, H);
        }
        if (req.method === 'GET' && path === '/admin/comments') {
          const s = url.searchParams.get('status');
          const st = s === 'all' ? null : ['pending', 'approved', 'rejected'].includes(s) ? s : 'pending';
          const q = st ? env.DB.prepare('SELECT * FROM comments WHERE status=? ORDER BY id DESC LIMIT 300').bind(st) : env.DB.prepare('SELECT * FROM comments ORDER BY id DESC LIMIT 300');
          const { results } = await q.all();
          return J({ comments: results }, 200, H);
        }
        const m = path.match(/^\/admin\/comments\/(\d+)$/);
        if (req.method === 'POST' && m) {
          const id = +m[1], b = await req.json().catch(() => ({})), c = await env.DB.prepare('SELECT * FROM comments WHERE id=?').bind(id).first();
          if (!c) return J({ error: 'non trovato' }, 404, H);
          if (b.action === 'approve') await env.DB.prepare("UPDATE comments SET status='approved' WHERE id=?").bind(id).run();
          else if (b.action === 'reject') await env.DB.prepare("UPDATE comments SET status='rejected', contact='' WHERE id=?").bind(id).run();
          else if (b.action === 'delete') await env.DB.prepare('DELETE FROM comments WHERE id=?').bind(id).run();
          else if (b.action === 'reply') {
            const reply = clean(b.reply, 1500); if (!reply) return J({ error: 'risposta vuota' }, 400, H);
            await env.DB.prepare("UPDATE comments SET reply=?, replied_at=?, status='approved' WHERE id=?").bind(reply, new Date().toISOString(), id).run();
            let sent = false;
            if (b.sendEmail && c.contact_type === 'email') sent = await mail(env, c.contact, `Risposta al tuo commento su «${c.poem_title}»`, `${reply}\n\nIl tuo commento: «${c.message}»\n${env.SITE_URL}/poesie/`);
            return J({ ok: true, emailSent: sent }, 200, H);
          } else return J({ error: 'azione sconosciuta' }, 400, H);
          return J({ ok: true }, 200, H);
        }
      }
      return J({ error: 'non trovato' }, 404, H);
    } catch (e) { console.error('errore', e && e.message); return J({ error: 'errore del servizio' }, 500, H); }
  },
  // ogni notte: i recapiti dei commenti più vecchi di 12 mesi vengono cancellati
  async scheduled(_e, env) {
    await env.DB.prepare("DELETE FROM seen WHERE day < ?").bind(new Date(Date.now() - 3 * 864e5).toISOString().slice(0, 10)).run();
    await env.DB.prepare("UPDATE comments SET contact='' WHERE contact<>'' AND created_at<?").bind(new Date(Date.now() - 365 * 864e5).toISOString()).run();
  },
};
