<h1>Послуги</h1>
<div class="cards">
<?php foreach ($services as $s): ?>
    <div class="card">
        <?php if ($s['image']): ?>
            <img src="<?= htmlspecialchars($s['image']) ?>"
                 alt="<?= htmlspecialchars($s['title']) ?>"
                 style="width:100%;height:160px;object-fit:cover;border-radius:6px;margin-bottom:.75rem">
        <?php endif; ?>
        <h2><?= htmlspecialchars($s['title']) ?></h2>
        <p><?= htmlspecialchars($s['description'] ?? '') ?></p>
        <span class="price"><?= number_format($s['price'], 0, '', "\xc2\xa0") ?> ₴</span><br><br>
        <a href="/services/<?= $s['slug'] ?>">Детальніше →</a>
    </div>
<?php endforeach; ?>
</div>
