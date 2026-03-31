<h1>Реєстрація</h1>
<?php if (!empty($errors)): ?>
    <ul style="color:red">
        <?php foreach ($errors as $e): ?>
            <li><?= htmlspecialchars($e) ?></li>
        <?php endforeach; ?>
    </ul>
<?php endif; ?>
<form method="POST" action="/register">
    <p><label>Ім'я<br>
        <input type="text" name="name" value="<?= htmlspecialchars($old['name'] ?? '') ?>" required>
    </label></p>
    <p><label>Email<br>
        <input type="email" name="email" value="<?= htmlspecialchars($old['email'] ?? '') ?>" required>
    </label></p>
    <p><label>Пароль<br>
        <input type="password" name="password" required>
    </label></p>
    <button type="submit" class="btn">Зареєструватись</button>
    <p><a href="/login">Вже є акаунт?</a></p>
</form>