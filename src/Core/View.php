<?php
class View {
    public static function render(string $template, array $data = [], string $layout = 'layout'): string {
        extract($data);
        ob_start();
        include __DIR__ . '/../Views/' . $template . '.php';
        $content = ob_get_clean();

        ob_start();
        include __DIR__ . '/../Views/' . $layout . '.php';
        return ob_get_clean();
    }
}