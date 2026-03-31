<h1>Вхід</h1>
<?php if (!empty($error)): ?>
    <p style="color:red"><?= htmlspecialchars($error) ?></p>
<?php endif; ?>
<form method="POST" action="/login">
    <p><label>Email<br>
        <input type="email" name="email" value="<?= htmlspecialchars($old['email'] ?? '') ?>" required>
    </label></p>
    <p><label>Пароль<br>
        <input type="password" name="password" required>
    </label></p>
    <button type="submit" class="btn">Увійти</button>
    <p><a href="/register">Ще немає акаунту?</a></p>
</form>