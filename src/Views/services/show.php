<?php if ($service['image']): ?>
    <img src="<?= htmlspecialchars($service['image']) ?>"
         alt="<?= htmlspecialchars($service['title']) ?>"
         style="width:100%;max-height:400px;object-fit:cover;border-radius:8px;margin-bottom:1.5rem">
<?php endif; ?>

<h1><?= htmlspecialchars($service['title']) ?></h1>

<?php if ($service['content']): ?>
    <div class="service-content">
        <?= (new Parsedown)->text($service['content']) ?>
    </div>
<?php else: ?>
    <p><?= htmlspecialchars($service['description'] ?? '') ?></p>
<?php endif; ?>

<p style="margin-top:1.5rem">
    <strong>Вартість:</strong>
    <?= number_format($service['price'], 0, '', "\u00a0") ?> ₴
</p>

<?php if (Auth::isUser()): ?>
    <form method="POST" action="/cart/add/<?= $service['id'] ?>">
        <button type="submit" class="btn" style="margin-top:1rem">
            🛒 Додати в кошик
        </button>
    </form>
    <p style="margin-top:.5rem"><a href="/cart">Перейти в кошик →</a></p>
<?php else: ?>
    <p style="margin-top:1rem">
        <a href="/login" class="btn">Увійдіть щоб замовити</a>
    </p>
<?php endif; ?>