// Servizio commenti per Il Libro dei Pensieri Muti — Cloudflare Worker + D1.
const J = (o, s = 200, h = {}) => new Response(JSON.stringify(o), { status: s, headers: { 'content-type': 'application/json', ...h } });
const cors = (env) => ({ 'access-control-allow-origin': env.SITE_ORIGIN, 'access-control-allow-headers': 'content-type, authorization', 'access-control-allow-methods': 'GET, POST, OPTIONS', vary: 'origin' });
const clean = (s, n) => String(s ?? '').replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F]/g, '').replace(/<[^>]*>/g, '').trim().slice(0, n);
const sha = async (t) => [...new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(t)))].map((b) => b.toString(16).padStart(2, '0')).join('');
const same = (a, b) => { if (a.length !== b.length) return false; let r = 0; for (let i = 0; i < a.length; i++) r |= a.charCodeAt(i) ^ b.charCodeAt(i); return r === 0; };

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
    } catch (e) { return J({ error: 'errore del servizio' }, 500, H); }
  },
  // ogni notte: i recapiti dei commenti più vecchi di 12 mesi vengono cancellati
  async scheduled(_e, env) {
    await env.DB.prepare("UPDATE comments SET contact='' WHERE contact<>'' AND created_at<?").bind(new Date(Date.now() - 365 * 864e5).toISOString()).run();
  },
};
