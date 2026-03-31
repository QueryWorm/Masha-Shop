<?php
class Env {
    private static array $data = [];

    public static function load(string $path): void {
        if (!file_exists($path)) return;
        foreach (file($path, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES) as $line) {
            if (str_starts_with(trim($line), '#')) continue;
            [$key, $value] = explode('=', $line, 2);
            self::$data[trim($key)] = trim($value);
        }
    }

    public static function get(string $key, string $default = ''): string {
        return self::$data[$key] ?? $default;
    }
}