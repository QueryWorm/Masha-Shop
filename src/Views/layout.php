<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <title><?= htmlspecialchars($title ?? 'Послуги') ?></title>
    <link rel="stylesheet" href="/style.css">
</head>
<body>
<nav>
    <a href="/">Головна</a>
    <a href="/services">Послуги</a>
    <?php if (Auth::isUser()): ?>
        <?php $cartCount = Cart::count(Auth::user()['id']); ?>
        <a href="/cart">🛒<?= $cartCount > 0 ? " ({$cartCount})" : '' ?></a>
        <a href="/account">Мої замовлення</a>
        <a href="/logout">Вийти</a>
    <?php else: ?>
        <a href="/login">Вхід</a>
        <a href="/register">Реєстрація</a>
    <?php endif; ?>
</nav>
<main>
<?= $content ?>
</main>
</body>
</html>