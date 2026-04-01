<?php
class LinkToken {
    public static function create(int $userId): string {
        $token = bin2hex(random_bytes(16));
        $expires = date('Y-m-d H:i:s', time() + 600); // 10 хвилин

        $stmt = Database::get()->prepare('
            INSERT INTO link_tokens (token, user_id, expires_at)
            VALUES (?, ?, ?)
        ');
        $stmt->execute([$token, $userId, $expires]);
        return $token;
    }

    public static function consume(string $token): ?int {
        $stmt = Database::get()->prepare('
            SELECT * FROM link_tokens
            WHERE token = ? AND expires_at > datetime("now")
        ');
        $stmt->execute([$token]);
        $row = $stmt->fetch();
        if (!$row) return null;

        // Видаляємо одноразовий токен
        Database::get()->prepare('DELETE FROM link_tokens WHERE token = ?')
            ->execute([$token]);

        return (int)$row['user_id'];
    }
}