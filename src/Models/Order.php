<?php
class Order {
    public static function create(int $serviceId, string $name, string $email): void {
        $stmt = Database::get()->prepare(
            'INSERT INTO orders (service_id, name, email) VALUES (?, ?, ?)'
        );
        $stmt->execute([$serviceId, $name, $email]);
    }
}