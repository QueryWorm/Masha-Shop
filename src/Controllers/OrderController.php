<?php
class OrderController {
    public function store(Request $request) {
        $name      = trim($request->post['name'] ?? '');
        $email     = trim($request->post['email'] ?? '');
        $serviceId = (int)($request->post['service_id'] ?? 0);

        if (!$name || !$email || !$serviceId) {
            return "Ошибка: заполните все поля";
        }

        Order::create($serviceId, $name, $email);

        return View::render('orders/thanks', [
            'title' => 'Заявка принята',
            'name'  => $name,
        ]);
    }
}