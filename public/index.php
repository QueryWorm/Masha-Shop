<?php
ini_set('display_errors', 1);
error_reporting(E_ALL);

require_once __DIR__ . '/../src/Core/Request.php';
require_once __DIR__ . '/../src/Core/Database.php';
require_once __DIR__ . '/../src/Core/View.php';
require_once __DIR__ . '/../src/Core/Auth.php';
require_once __DIR__ . '/../src/Router.php';
require_once __DIR__ . '/../src/Models/Service.php';
require_once __DIR__ . '/../src/Models/Order.php';
require_once __DIR__ . '/../src/Models/User.php';
require_once __DIR__ . '/../src/Controllers/ServiceController.php';
require_once __DIR__ . '/../src/Controllers/OrderController.php';
require_once __DIR__ . '/../src/Controllers/AuthController.php';
require_once __DIR__ . '/../src/Controllers/AccountController.php';
require_once __DIR__ . '/../src/Controllers/AdminController.php';
require_once __DIR__ . '/../src/Models/Cart.php';
require_once __DIR__ . '/../src/Controllers/CartController.php';
require_once __DIR__ . '/../src/Models/Cart.php';
require_once __DIR__ . '/../src/Controllers/CartController.php';
require_once __DIR__ . '/../src/Core/Parsedown.php';
require_once __DIR__ . '/../src/Core/ImageUploader.php';

Auth::start();

$request  = new Request();
$router   = new Router();

$services = new ServiceController();
$orders   = new OrderController();
$auth     = new AuthController();
$account  = new AccountController();
$admin    = new AdminController();

// Публічні
$router->get('/',                  fn() => View::render('services/index', [
    'title'    => 'Послуги',
    'services' => Service::all(),
]));
$router->get('/services',          [$services, 'index']);
$router->get('/services/{slug}',   [$services, 'show']);
$router->post('/order',            [$orders,   'store']);

// Авторизація
$router->get('/register',          [$auth,    'registerForm']);
$router->post('/register',         [$auth,    'register']);
$router->get('/login',             [$auth,    'loginForm']);
$router->post('/login',            [$auth,    'login']);
$router->get('/logout',            [$auth,    'logout']);

// Кабінет клієнта
$router->get('/account',           [$account, 'orders']);

// Адмін
$router->get('/admin/login',       [$admin,   'loginForm']);
$router->post('/admin/login',      [$admin,   'login']);
$router->get('/admin',             [$admin,   'dashboard']);
$router->get('/admin/orders',      [$admin,   'orders']);
$router->post('/admin/orders/{id}/status', [$admin, 'updateOrderStatus']);
$router->get('/admin/services',    [$admin,   'services']);
$router->post('/admin/services/{id}', [$admin, 'updateService']);

// Кошик
$cart = new CartController();
$router->get('/cart',              [$cart, 'show']);
$router->post('/cart/add/{id}',    [$cart, 'add']);
$router->post('/cart/remove/{id}', [$cart, 'remove']);
$router->post('/cart/checkout',    [$cart, 'checkout']);
echo $router->handle($request);