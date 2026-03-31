<div>
    <div class="stat">
        <h3>Всього замовлень</h3>
        <p><?= $total['cnt'] ?></p>
    </div>
    <div class="stat">
        <h3>Сума</h3>
        <p><?= number_format($total['sum'] ?? 0, 0, '', ' ') ?> ₴</p>
    </div>
    <div class="stat">
        <h3>Нових</h3>
        <p><?= $new['cnt'] ?></p>
    </div>
    <div class="stat">
        <h3>Виконано</h3>
        <p><?= $done['cnt'] ?></p>
    </div>
</div>
<br>
<a href="/admin/orders?status=new" class="btn">Нові замовлення →</a>
