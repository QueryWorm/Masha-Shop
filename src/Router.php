<?php
class Router {
    private array $routes = [];

    public function get(string $path, mixed $handler): void {
        $this->routes['GET'][$path] = $handler;
    }

    public function post(string $path, mixed $handler): void {
        $this->routes['POST'][$path] = $handler;
    }

    public function handle(Request $request): string {
        $method = $request->method;
        $uri    = $request->uri;

        // Сначала ищем точное совпадение
        if (isset($this->routes[$method][$uri])) {
            return call_user_func($this->routes[$method][$uri], $request);
        }

        // Потом ищем маршруты с параметрами: /services/{slug}
        foreach ($this->routes[$method] ?? [] as $path => $handler) {
            $pattern = preg_replace('/\{[^}]+\}/', '([^/]+)', $path);
            $pattern = '#^' . $pattern . '$#';
            if (preg_match($pattern, $uri, $matches)) {
                array_shift($matches); // убираем полное совпадение
                return call_user_func($handler, $request, ...$matches);
            }
        }

        return "404 — страница не найдена";
    }
}