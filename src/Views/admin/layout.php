<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <title>Адмін — <?= htmlspecialchars($title ?? '') ?></title>
    <style>
        body { font-family: sans-serif; margin: 0; background: #f4f4f4; }
        .sidebar { width: 200px; background: #1a1a2e; color: #fff; min-height: 100vh;
                   position: fixed; padding: 1rem; }
        .sidebar a { display: block; color: #aaa; text-decoration: none;
                     padding: .5rem 0; margin-bottom: .3rem; }
        .sidebar a:hover { color: #fff; }
        .sidebar h2 { color: #fff; font-size: 1rem; margin-bottom: 1.5rem; }
        .main { margin-left: 220px; padding: 2rem; }
        table { width: 100%; border-collapse: collapse; background: #fff; }
        th, td { padding: .6rem 1rem; text-align: left; border-bottom: 1px solid #eee; }
        th { background: #f0f0f0; }
        .btn { background: #4f46e5; color: #fff; border: none; padding: .4rem 1rem;
               border-radius: 6px; cursor: pointer; text-decoration: none;
               display: inline-block; font-size: .9rem; }
        .stat { background: #fff; border-radius: 8px; padding: 1.5rem;
                display: inline-block; margin-right: 1rem; min-width: 150px; }
        .stat h3 { margin: 0 0 .5rem; font-size: .9rem; color: #666; }
        .stat p { margin: 0; font-size: 1.8rem; font-weight: bold; }
    </style>
</head>
<body>
<div class="sidebar">
    <h2>⚙️ Адмін</h2>
    <a href="/admin">📊 Дашборд</a>
    <a href="/admin/orders">📋 Замовлення</a>
    <a href="/admin/services">🛍 Послуги</a>
    <a href="/" style="margin-top:2rem">← Сайт</a>
    <a href="/logout">Вийти</a>
</div>
<div class="main">
    <h1><?= htmlspecialchars($title ?? '') ?></h1>
    <?= $content ?>
</div>
</body>
</html>