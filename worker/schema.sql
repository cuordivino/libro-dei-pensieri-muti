CREATE TABLE IF NOT EXISTS comments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  poem_id INTEGER NOT NULL, poem_title TEXT NOT NULL,
  name TEXT NOT NULL, message TEXT NOT NULL,
  contact_type TEXT NOT NULL DEFAULT 'none', contact TEXT NOT NULL DEFAULT '',
  public INTEGER NOT NULL DEFAULT 1,
  status TEXT NOT NULL DEFAULT 'pending',          -- pending | approved | rejected
  reply TEXT, replied_at TEXT,
  consent_at TEXT NOT NULL, created_at TEXT NOT NULL, ip_hash TEXT
);
CREATE INDEX IF NOT EXISTS idx_poem_status ON comments (poem_id, status);
CREATE INDEX IF NOT EXISTS idx_ip ON comments (ip_hash, created_at);
