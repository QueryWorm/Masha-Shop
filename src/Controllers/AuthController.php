<?php
class AuthController {
    public function registerForm(): string {
        return View::render('auth/register', ['title' => 'Реєстрація']);
    }

    public function register(Request $request): string {
        $name     = trim($request->post['name'] ?? '');
        $email    = trim($request->post['email'] ?? '');
        $password = $request->post['password'] ?? '';
        $errors   = [];

        if (!$name)                                      $errors[] = "Вкажіть ім'я";
        if (!filter_var($email, FILTER_VALIDATE_EMAIL))  $errors[] = "Невірний email";
        if (strlen($password) < 6)                       $errors[] = "Пароль мінімум 6 символів";
        if (User::emailExists($email))                   $errors[] = "Email вже зареєстрований";

        if ($errors) {
            return View::render('auth/register', [
                'title'  => 'Реєстрація',
                'errors' => $errors,
                'old'    => ['name' => $name, 'email' => $email],
            ]);
        }

        $user = User::createWithPassword($email, $name, $password);
        Auth::loginUser($user);
        header('Location: /account');
        exit;
    }

    public function loginForm(): string {
        return View::render('auth/login', ['title' => 'Вхід']);
    }

    public function login(Request $request): string {
        $email    = trim($request->post['email'] ?? '');
        $password = $request->post['password'] ?? '';

        $user = User::verifyPassword($email, $password);
        if (!$user) {
            return View::render('auth/login', [
                'title' => 'Вхід',
                'error' => 'Невірний email або пароль',
                'old'   => ['email' => $email],
            ]);
        }

        Auth::loginUser($user);
        header('Location: ' . (Auth::isAdmin() ? '/admin' : '/account'));
        exit;
    }

    public function logout(): void {
        Auth::logout();
    }
}