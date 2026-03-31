-- Нова таблиця користувачів (замінює стару users)
CREATE TABLE IF NOT EXISTS users_new (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    email      TEXT,
    name       TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

-- Способи входу
CREATE TABLE IF NOT EXISTS auth_providers (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users_new(id),
    provider    TEXT NOT NULL,
    provider_id TEXT NOT NULL,
    created_at  TEXT DEFAULT (datetime('now')),
    UNIQUE(provider, provider_id)
);

-- Мігруємо існуючих users → users_new + auth_providers
INSERT INTO users_new (id, email, name, created_at)
    SELECT id, email, name, created_at FROM users;

INSERT INTO auth_providers (user_id, provider, provider_id)
    SELECT id, 'password', email FROM users;

-- Мігруємо tg_users → users_new + auth_providers
INSERT INTO users_new (name)
    SELECT COALESCE(saved_name, first_name)
    FROM tg_users
    WHERE chat_id NOT IN (
        SELECT CAST(provider_id AS INTEGER)
        FROM auth_providers WHERE provider = 'telegram'
    );

INSERT INTO auth_providers (user_id, provider, provider_id)
    SELECT u.id, 'telegram', t.chat_id
    FROM tg_users t
    JOIN users_new u ON u.name = COALESCE(t.saved_name, t.first_name)
    WHERE t.chat_id NOT IN (
        SELECT CAST(provider_id AS INTEGER)
        FROM auth_providers WHERE provider = 'telegram'
    );

-- Перейменовуємо таблиці
ALTER TABLE users RENAME TO users_old;
ALTER TABLE users_new RENAME TO users;

-- Оновлюємо orders — додаємо user_id якщо нема
-- (вже є з попередньої міграції)

-- Таблиця паролів окремо (password_hash не в users)
CREATE TABLE IF NOT EXISTS user_passwords (
    user_id       INTEGER PRIMARY KEY REFERENCES users(id),
    password_hash TEXT NOT NULL
);

INSERT INTO user_passwords (user_id, password_hash)
    SELECT id, password FROM users_old;