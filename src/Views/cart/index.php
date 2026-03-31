<?php $user = Auth::user(); ?>

<?php if (empty($items)): ?>
    <p>Кошик порожній. <a href="/services">Обрати послугу →</a></p>
<?php else: ?>
    <table width="100%" cellpadding="8" style="border-collapse:collapse">
        <tr>
            <th style="text-align:left;border-bottom:1px solid #ddd">Послуга</th>
            <th style="text-align:right;border-bottom:1px solid #ddd">Ціна</th>
            <th style="border-bottom:1px solid #ddd"></th>
        </tr>
        <?php foreach ($items as $item): ?>
        <tr>
            <td><?= htmlspecialchars($item['title']) ?></td>
            <td style="text-align:right"><?= number_format($item['price'], 0, '', "\u00a0") ?> ₴</td>
            <td style="text-align:right">
                <form method="POST" action="/cart/remove/<?= $item['service_id'] ?>">
                    <button type="submit" style="background:none;border:none;color:#e53e3e;cursor:pointer">✕</button>
                </form>
            </td>
        </tr>
        <?php endforeach; ?>
        <tr>
            <td><strong>Разом</strong></td>
            <td style="text-align:right"><strong><?= number_format($total, 0, '', "\u00a0") ?> ₴</strong></td>
            <td></td>
        </tr>
    </table>

    <?php if (!empty($error)): ?>
        <p style="color:red"><?= htmlspecialchars($error) ?></p>
    <?php endif; ?>

    <form method="POST" action="/cart/checkout" style="margin-top:1.5rem">
        <?php if (empty($user['email'])): ?>
            <p>
                <label>Email для зв'язку<br>
                    <input type="email" name="email" required style="width:100%;max-width:360px;padding:.4rem">
                </label>
            </p>
        <?php endif; ?>
        <button type="submit" class="btn">Оформити замовлення</button>
        <a href="/services" style="margin-left:1rem">← Додати ще</a>
    </form>
<?php endif; ?>
