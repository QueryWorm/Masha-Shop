<?php
class AdminController {
    public function loginForm(): string {
        return View::render('admin/login', ['title' => 'Адмін'], 'admin/layout');
    }

    public function login(Request $request): string {
        $email    = trim($request->post['email'] ?? '');
        $password = $request->post['password'] ?? '';

        $user = User::verifyPassword($email, $password);

        if (!$user || $user['role'] !== 'admin') {
            return View::render('admin/login', [
                'title' => 'Адмін',
                'error' => 'Невірний email або пароль',
            ], 'admin/layout');
        }

        Auth::loginUser($user);
        header('Location: /admin');
        exit;
    }

    public function dashboard(): string {
        Auth::requireAdmin();
        $db    = Database::get();
        $total = $db->query('SELECT COUNT(*) as cnt, COALESCE(SUM(s.price),0) as sum
                             FROM orders o JOIN services s ON o.service_id = s.id')->fetch();
        $new   = $db->query('SELECT COUNT(*) as cnt FROM orders WHERE status = "new"')->fetch();
        $done  = $db->query('SELECT COUNT(*) as cnt FROM orders WHERE status = "done"')->fetch();

        return View::render('admin/dashboard', [
            'title' => 'Дашборд',
            'total' => $total,
            'new'   => $new,
            'done'  => $done,
        ], 'admin/layout');
    }

    public function orders(): string {
        Auth::requireAdmin();
        $status = $_GET['status'] ?? null;
        $query  = 'SELECT o.*, s.title as service_title
                   FROM orders o JOIN services s ON o.service_id = s.id';
        if ($status) {
            $stmt = Database::get()->prepare($query . ' WHERE o.status = ? ORDER BY o.id DESC');
            $stmt->execute([$status]);
        } else {
            $stmt = Database::get()->query($query . ' ORDER BY o.id DESC');
        }
        return View::render('admin/orders', [
            'title'  => 'Замовлення',
            'orders' => $stmt->fetchAll(),
            'status' => $status,
        ], 'admin/layout');
    }

    public function updateOrderStatus(Request $request, string $id): string {
        Auth::requireAdmin();
        $status  = $request->post['status'] ?? '';
        $allowed = ['new', 'in_progress', 'done', 'cancelled'];
        if (in_array($status, $allowed)) {
            $stmt = Database::get()->prepare('UPDATE orders SET status = ? WHERE id = ?');
            $stmt->execute([$status, (int)$id]);
        }
        header('Location: /admin/orders');
        exit;
    }

    public function services(): string {
        Auth::requireAdmin();
        return View::render('admin/services', [
            'title'    => 'Послуги',
            'services' => Service::all(),
        ], 'admin/layout');
    }    
    public function updateService(Request $request, string $id): string {
        Auth::requireAdmin();
    
        $service = Service::findById((int)$id);
        if (!$service) {
            return "Послугу не знайдено";
        }
    
        $image = $service['image']; // залишаємо старе якщо нове не завантажили
    
        if (!empty($_FILES['image']['name'])) {
            try {
                // Видаляємо старе фото
                if ($image) ImageUploader::delete($image);
                $image = ImageUploader::upload($_FILES['image']);
            } catch (RuntimeException $e) {
                return View::render('admin/services', [
                    'title'    => 'Послуги',
                    'services' => Service::all(),
                    'error'    => $e->getMessage(),
                ], 'admin/layout');
            }
        }

        Service::update((int)$id, [
            'title'       => trim($request->post['title'] ?? ''),
            'description' => trim($request->post['description'] ?? ''),
            'content'     => trim($request->post['content'] ?? ''),
            'price'       => (int)($request->post['price'] ?? 0),
            'image'       => $image,
        ]);
    
        header('Location: /admin/services');
        exit;
    }
    
}