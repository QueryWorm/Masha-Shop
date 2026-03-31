<?php
class Request {
    public string $method;
    public string $uri;
    public array $get;
    public array $post;
    public function __construct() {
        $this->method = $_SERVER['REQUEST_METHOD'];
        $uri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
        $this->uri = rtrim($uri, '/') ?: '/';
        $this->get = $_GET;
        $this->post = $_POST;
    }
}
