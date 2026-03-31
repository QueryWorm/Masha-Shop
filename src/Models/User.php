<?php
class User {
    // Знайти користувача за провайдером
    public static function findByProvider(string $provider, string $providerId): ?array {
        $stmt = Database::get()->prepare('
            SELECT u.* FROM users u
            JOIN auth_providers ap ON ap.user_id = u.id
            WHERE ap.provider = ? AND ap.provider_id = ?
        ');
        $stmt->execute([$provider, $providerId]);
        return $stmt->fetch() ?: null;
    }

    // Знайти за email (для входу паролем)
    public static function findByEmail(string $email): ?array {
        $stmt = Database::get()->prepare('SELECT * FROM users WHERE email = ?');
        $stmt->execute([$email]);
        return $stmt->fetch() ?: null;
    }

    // Реєстрація через email + пароль
    public static function createWithPassword(string $email, string $name, string $password): array {
        $db = Database::get();

        $stmt = $db->prepare('INSERT INTO users (email, name, role) VALUES (?, ?, ?)');
        $stmt->execute([$email, $name, 'client']);
        $userId = (int)$db->lastInsertId();

        // Провайдер
        $stmt = $db->prepare('INSERT INTO auth_providers (user_id, provider, provider_id) VALUES (?, ?, ?)');
        $stmt->execute([$userId, 'password', $email]);

        // Пароль окремо
        $stmt = $db->prepare('INSERT INTO user_passwords (user_id, password_hash) VALUES (?, ?)');
        $stmt->execute([$userId, password_hash($password, PASSWORD_DEFAULT)]);

        return self::findByEmail($email);
    }

    // Реєстрація/вхід через Telegram
    public static function upsertTelegram(int $chatId, string $name): array {
        $existing = self::findByProvider('telegram', (string)$chatId);
        if ($existing) {
            return $existing;
        }

        $db = Database::get();
        $stmt = $db->prepare('INSERT INTO users (name, role) VALUES (?, ?)');
        $stmt->execute([$name, 'client']);
        $userId = (int)$db->lastInsertId();

        $stmt = $db->prepare('INSERT INTO auth_providers (user_id, provider, provider_id) VALUES (?, ?, ?)');
        $stmt->execute([$userId, 'telegram', (string)$chatId]);

        return self::findByProvider('telegram', (string)$chatId);
    }

    // Перевірка пароля
    public static function verifyPassword(string $email, string $password): ?array {
        $user = self::findByEmail($email);
        if (!$user) return null;

        $stmt = Database::get()->prepare('SELECT password_hash FROM user_passwords WHERE user_id = ?');
        $stmt->execute([$user['id']]);
        $row = $stmt->fetch();

        if ($row && password_verify($password, $row['password_hash'])) {
            return $user;
        }
        return null;
    }

    // Оновити ім'я для Telegram користувача
    public static function updateName(int $userId, string $name): void {
        $stmt = Database::get()->prepare('UPDATE users SET name = ? WHERE id = ?');
        $stmt->execute([$name, $userId]);
    }

    public static function emailExists(string $email): bool {
        $stmt = Database::get()->prepare('SELECT id FROM users WHERE email = ?');
        $stmt->execute([$email]);
        return (bool)$stmt->fetch();
    }
}