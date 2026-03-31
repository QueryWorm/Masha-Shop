<?php
class Auth {
    public static function start(): void {
        if (session_status() === PHP_SESSION_NONE) {
            session_start();
        }
    }

    public static function loginUser(array $user): void {
        $_SESSION['user_id']   = $user['id'];
        $_SESSION['user_email'] = $user['email'] ?? '';
        $_SESSION['user_name'] = $user['name'];
        $_SESSION['user_role'] = $user['role'];
    }

    public static function user(): ?array {
        if (empty($_SESSION['user_id'])) return null;
        return [
            'id'    => $_SESSION['user_id'],
            'email' => $_SESSION['user_email'],
            'name'  => $_SESSION['user_name'],
            'role'  => $_SESSION['user_role'],
        ];
    }

    public static function isUser(): bool {
        return !empty($_SESSION['user_id']);
    }

    public static function isAdmin(): bool {
        return ($_SESSION['user_role'] ?? '') === 'admin';
    }

    public static function requireUser(): void {
        if (!self::isUser()) {
            header('Location: /login');
            exit;
        }
    }

    public static function requireAdmin(): void {
        if (!self::isAdmin()) {
            header('Location: /admin/login');
            exit;
        }
    }

    public static function logout(): void {
        session_destroy();
        header('Location: /');
        exit;
    }
}