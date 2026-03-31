<?php
class CartController {
    public function show(): string {
        Auth::requireUser();
        $user  = Auth::user();
        $items = Cart::get($user['id']);
        return View::render('cart/index', [
            'title' => 'Кошик',
            'items' => $items,
            'total' => Cart::total($items),
        ]);
    }

    public function add(Request $request, string $serviceId): string {
        Auth::requireUser();
        $user = Auth::user();
        Cart::add($user['id'], (int)$serviceId);
        header('Location: /cart');
        exit;
    }

    public function remove(Request $request, string $serviceId): string {
        Auth::requireUser();
        $user = Auth::user();
        Cart::remove($user['id'], (int)$serviceId);
        header('Location: /cart');
        exit;
    }

    public function checkout(Request $request): string {
        Auth::requireUser();
        $user  = Auth::user();
        $items = Cart::get($user['id']);

        if (empty($items)) {
            header('Location: /cart');
            exit;
        }

        $name  = $user['name'];
        $email = $user['email'] ?? trim($request->post['email'] ?? '');

        if (!$email) {
            return View::render('cart/index', [
                'title'       => 'Кошик',
                'items'       => $items,
                'total'       => Cart::total($items),
                'error'       => 'Вкажіть email для оформлення',
            ]);
        }

        // Створюємо замовлення на кожну послугу
        $db = Database::get();
        foreach ($items as $item) {
            $stmt = $db->prepare('
                INSERT INTO orders (service_id, user_id, name, email)
                VALUES (?, ?, ?, ?)
            ');
            $stmt->execute([$item['service_id'], $user['id'], $name, $email]);
        }

        Cart::clear($user['id']);

        return View::render('cart/thanks', [
            'title' => 'Замовлення оформлено',
            'count' => count($items),
            'name'  => $name,
        ]);
    }
}