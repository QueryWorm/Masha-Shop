<?php
class ImageUploader {
    private static string $uploadDir = __DIR__ . '/../../public/uploads/services/';
    private static int $maxSize      = 2 * 1024 * 1024; // 2MB
    private static array $allowed    = ['image/jpeg', 'image/png', 'image/webp'];
    private static int $maxWidth     = 1200;
    private static int $maxHeight    = 800;

    public static function upload(array $file): string {
        if ($file['error'] !== UPLOAD_ERR_OK) {
            throw new RuntimeException('Помилка завантаження файлу');
        }
        if ($file['size'] > self::$maxSize) {
            throw new RuntimeException('Файл занадто великий. Максимум 2MB');
        }

        $mime = mime_content_type($file['tmp_name']);
        if (!in_array($mime, self::$allowed)) {
            throw new RuntimeException('Дозволені тільки JPG, PNG, WebP');
        }

        $ext      = match($mime) {
            'image/jpeg' => 'jpg',
            'image/png'  => 'png',
            'image/webp' => 'webp',
        };
        $filename = uniqid('service_', true) . '.' . $ext;
        $destPath = self::$uploadDir . $filename;

        self::resizeAndSave($file['tmp_name'], $destPath, $mime);

        return '/uploads/services/' . $filename;
    }

    private static function resizeAndSave(string $src, string $dest, string $mime): void {
        $image = match($mime) {
            'image/jpeg' => imagecreatefromjpeg($src),
            'image/png'  => imagecreatefrompng($src),
            'image/webp' => imagecreatefromwebp($src),
        };

        [$w, $h] = getimagesize($src);

        // Якщо вже менше максимуму — просто копіюємо
        if ($w <= self::$maxWidth && $h <= self::$maxHeight) {
            move_uploaded_file($src, $dest);
            imagedestroy($image);
            return;
        }

        // Рахуємо новий розмір зі збереженням пропорцій
        $ratio  = min(self::$maxWidth / $w, self::$maxHeight / $h);
        $newW   = (int)($w * $ratio);
        $newH   = (int)($h * $ratio);

        $resized = imagecreatetruecolor($newW, $newH);

        // Прозорість для PNG
        if ($mime === 'image/png') {
            imagealphablending($resized, false);
            imagesavealpha($resized, true);
        }

        imagecopyresampled($resized, $image, 0, 0, 0, 0, $newW, $newH, $w, $h);

        match($mime) {
            'image/jpeg' => imagejpeg($resized, $dest, 85),
            'image/png'  => imagepng($resized, $dest, 6),
            'image/webp' => imagewebp($resized, $dest, 85),
        };

        imagedestroy($image);
        imagedestroy($resized);
    }

    public static function delete(string $path): void {
        if (!$path) return;
        $full = __DIR__ . '/../../public' . $path;
        if (file_exists($full)) unlink($full);
    }
}
