CREATE TABLE IF NOT EXISTS tg_sessions (
    chat_id  INTEGER PRIMARY KEY,
    state    TEXT    NOT NULL DEFAULT 'idle',
    data     TEXT    NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS users (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    email      TEXT UNIQUE NOT NULL,
    password   TEXT NOT NULL,
    name       TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS admins (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    email      TEXT UNIQUE NOT NULL,
    password   TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS services (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    slug        TEXT    UNIQUE NOT NULL,
    title       TEXT    NOT NULL,
    description TEXT,
    price       INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS orders (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    service_id INTEGER NOT NULL,
    name       TEXT    NOT NULL,
    email      TEXT    NOT NULL,
    status     TEXT    NOT NULL DEFAULT 'new',
    created_at TEXT    DEFAULT (datetime('now')),
    FOREIGN KEY (service_id) REFERENCES services(id)
);

INSERT OR IGNORE INTO services (slug, title, description, price) VALUES
  ('analytics',   'Аналитика',     'Дашборды и отчёты в Excel/Google Sheets', 3000),
  ('pentest',     'Пентест',       'Проверка безопасности сайта и сети',       10000),
  ('automation',  'Автоматизация', 'Скрипты, боты, парсеры',                  5000),
  ('excel',       'Excel/Sheets',  'Формулы, макросы, VBA, Apps Script',       2000);