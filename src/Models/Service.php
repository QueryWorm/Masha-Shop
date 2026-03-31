<?php
class Service {
    public static function all(): array {
        return Database::get()
            ->query('SELECT * FROM services ORDER BY id')
            ->fetchAll();
    }

    public static function findBySlug(string $slug): ?array {
        $stmt = Database::get()->prepare('SELECT * FROM services WHERE slug = ?');
        $stmt->execute([$slug]);
        return $stmt->fetch() ?: null;
    }

    public static function findById(int $id): ?array {
        $stmt = Database::get()->prepare('SELECT * FROM services WHERE id = ?');
        $stmt->execute([$id]);
        return $stmt->fetch() ?: null;
    }

    public static function update(int $id, array $data): void {
        $stmt = Database::get()->prepare('
            UPDATE services
            SET title = ?, description = ?, content = ?, price = ?, image = ?
            WHERE id = ?
        ');
        $stmt->execute([
            $data['title'],
            $data['description'],
            $data['content'],
            $data['price'],
            $data['image'],
            $id,
        ]);
    }
}