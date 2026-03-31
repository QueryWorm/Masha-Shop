<?php
class AccountController {
    public function orders(): string {
        Auth::requireUser();
        $user = Auth::user();

        $stmt = Database::get()->prepare(
            'SELECT o.*, s.title as service_title
             FROM orders o
             JOIN services s ON o.service_id = s.id
             WHERE o.user_id = ?
             ORDER BY o.id DESC'
        );
        $stmt->execute([$user['id']]);
        $orders = $stmt->fetchAll();

        return View::render('account/orders', [
            'title'  => 'Мої замовлення',
            'user'   => $user,
            'orders' => $orders,
        ]);
    }
}