<?php
class Cart {
    public static function add(int $userId, int $serviceId): void {
        $stmt = Database::get()->prepare('
            INSERT OR IGNORE INTO cart_items (user_id, service_id)
            VALUES (?, ?)
        ');
        $stmt->execute([$userId, $serviceId]);
    }

    public static function remove(int $userId, int $serviceId): void {
        $stmt = Database::get()->prepare('
            DELETE FROM cart_items WHERE user_id = ? AND service_id = ?
        ');
        $stmt->execute([$userId, $serviceId]);
    }

    public static function get(int $userId): array {
        $stmt = Database::get()->prepare('
            SELECT ci.*, s.title, s.description, s.price, s.slug
            FROM cart_items ci
            JOIN services s ON s.id = ci.service_id
            WHERE ci.user_id = ?
            ORDER BY ci.created_at
        ');
        $stmt->execute([$userId]);
        return $stmt->fetchAll();
    }

    public static function clear(int $userId): void {
        $stmt = Database::get()->prepare('DELETE FROM cart_items WHERE user_id = ?');
        $stmt->execute([$userId]);
    }

    public static function total(array $items): int {
        return array_sum(array_column($items, 'price'));
    }

    public static function count(int $userId): int {
        $stmt = Database::get()->prepare('
            SELECT COUNT(*) FROM cart_items WHERE user_id = ?
        ');
        $stmt->execute([$userId]);
        return (int)$stmt->fetchColumn();
    }
}