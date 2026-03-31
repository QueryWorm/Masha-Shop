<?php if (!empty($error)): ?>
    <p style="color:red"><?= htmlspecialchars($error) ?></p>
<?php endif; ?>
<form method="POST" action="/admin/login" style="max-width:360px">
    <p><label>Email<br>
        <input type="email" name="email" required style="width:100%;padding:.4rem">
    </label></p>
    <p><label>Пароль<br>
        <input type="password" name="password" required style="width:100%;padding:.4rem">
    </label></p>
    <button type="submit" class="btn">Увійти</button>
</form>
