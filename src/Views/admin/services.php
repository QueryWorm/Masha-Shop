<?php if (!empty($error)): ?>
    <p style="color:red"><?= htmlspecialchars($error) ?></p>
<?php endif; ?>

<?php foreach ($services as $s): ?>
<details style="margin-bottom:1.5rem;background:#fff;border:1px solid #ddd;border-radius:8px;padding:1rem">
    <summary style="cursor:pointer;font-weight:bold;font-size:1.1rem">
        #<?= $s['id'] ?> <?= htmlspecialchars($s['title']) ?>
        — <?= number_format($s['price'], 0, '', ' ') ?> ₴
    </summary>

    <form method="POST" action="/admin/services/<?= $s['id'] ?>"
          enctype="multipart/form-data" style="margin-top:1rem">

        <p><label>Назва<br>
            <input type="text" name="title"
                   value="<?= htmlspecialchars($s['title']) ?>"
                   style="width:100%;padding:.4rem">
        </label></p>

        <p><label>Короткий опис (для превью і Telegram)<br>
            <textarea name="description" rows="3"
                      style="width:100%;padding:.4rem"><?= htmlspecialchars($s['description'] ?? '') ?></textarea>
        </label></p>

        <p><label>Повний опис (Markdown)<br>
            <textarea name="content" rows="12"
                      style="width:100%;padding:.4rem;font-family:monospace"><?= htmlspecialchars($s['content'] ?? '') ?></textarea>
        </label></p>
        <p style="font-size:.85rem;color:#666">
            Підтримується Markdown: **жирний**, *курсив*, ## заголовок, - список, ![alt](url)
        </p>

        <p><label>Ціна (₴)<br>
            <input type="number" name="price"
                   value="<?= $s['price'] ?>"
                   style="width:150px;padding:.4rem">
        </label></p>

        <p><label>Головне зображення<br>
            <?php if ($s['image']): ?>
                <img src="<?= htmlspecialchars($s['image']) ?>"
                     style="display:block;max-width:300px;margin:.5rem 0;border-radius:6px">
            <?php endif; ?>
            <input type="file" name="image" accept="image/jpeg,image/png,image/webp">
        </label></p>
        <p style="font-size:.85rem;color:#666">JPG, PNG або WebP, максимум 2MB</p>

        <button type="submit" class="btn">Зберегти</button>
    </form>
</details>
<?php endforeach; ?>