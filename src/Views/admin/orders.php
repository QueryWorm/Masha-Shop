<p>
    <a href="/admin/orders">Всі</a> |
    <a href="/admin/orders?status=new">Нові</a> |
    <a href="/admin/orders?status=in_progress">В роботі</a> |
    <a href="/admin/orders?status=done">Готово</a>
</p>
<?php if (empty($orders)): ?>
    <p>Замовлень немає.</p>
<?php else: ?>
<table>
    <tr><th>#</th><th>Послуга</th><th>Ім'я</th><th>Email</th><th>Статус</th><th>Дата</th><th></th></tr>
    <?php foreach ($orders as $o): ?>
    <tr>
        <td><?= $o['id'] ?></td>
        <td><?= htmlspecialchars($o['service_title']) ?></td>
        <td><?= htmlspecialchars($o['name']) ?></td>
        <td><?= htmlspecialchars($o['email']) ?></td>
        <td>
            <form method="POST" action="/admin/orders/<?= $o['id'] ?>/status">
                <select name="status" onchange="this.form.submit()">
                    <?php foreach (['new'=>'Нове','in_progress'=>'В роботі','done'=>'Готово','cancelled'=>'Скасовано'] as $val=>$label): ?>
                        <option value="<?= $val ?>" <?= $o['status']===$val?'selected':'' ?>><?= $label ?></option>
                    <?php endforeach; ?>
                </select>
            </form>
        </td>
        <td><?= $o['created_at'] ?></td>
    </tr>
    <?php endforeach; ?>
</table>
<?php endif; ?>
