<h1>Мої замовлення</h1>
<p>Привіт, <?= htmlspecialchars($user['name']) ?>! <a href="/logout">Вийти</a></p>

<?php if (empty($orders)): ?>
    <p>Замовлень ще немає. <a href="/services">Обрати послугу →</a></p>
<?php else: ?>
    <table width="100%" cellpadding="8" border="1" style="border-collapse:collapse">
        <tr><th>#</th><th>Послуга</th><th>Статус</th><th>Дата</th></tr>
        <?php foreach ($orders as $o): ?>
        <tr>
            <td><?= $o['id'] ?></td>
            <td><?= htmlspecialchars($o['service_title']) ?></td>
            <td><?= htmlspecialchars($o['status']) ?></td>
            <td><?= $o['created_at'] ?></td>
        </tr>
        <?php endforeach; ?>
    </table>
<?php endif; ?>