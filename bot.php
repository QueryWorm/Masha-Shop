<?php
require_once __DIR__ . '/src/Core/Env.php';
require_once __DIR__ . '/src/Core/Database.php';
require_once __DIR__ . '/src/Core/Telegram.php';
require_once __DIR__ . '/src/Models/Service.php';
require_once __DIR__ . '/src/Models/Order.php';

Env::load(__DIR__ . '/.env');

$tg      = new Telegram(Env::get('TG_TOKEN'));
$adminId = (int) Env::get('TG_ADMIN_CHAT_ID');
$offset  = 0;

echo "Бот запущен...\n";

// Инициализация таблицы сессий
Database::get()->exec("CREATE TABLE IF NOT EXISTS tg_sessions (
    chat_id INTEGER PRIMARY KEY,
    state   TEXT NOT NULL DEFAULT 'idle',
    data    TEXT NOT NULL DEFAULT '{}'
)");

function getSession(int $chatId): array {
    $stmt = Database::get()->prepare('SELECT * FROM tg_sessions WHERE chat_id = ?');
    $stmt->execute([$chatId]);
    $row = $stmt->fetch();
    if (!$row) return ['state' => 'idle', 'data' => []];
    return ['state' => $row['state'], 'data' => json_decode($row['data'], true)];
}

function setSession(int $chatId, string $state, array $data = []): void {
    $stmt = Database::get()->prepare('
        INSERT INTO tg_sessions (chat_id, state, data)
        VALUES (?, ?, ?)
        ON CONFLICT(chat_id) DO UPDATE SET state=excluded.state, data=excluded.data
    ');
    $stmt->execute([$chatId, $state, json_encode($data)]);
}

function showServices(Telegram $tg, int $chatId): void {
    $services = Service::all();
    $keyboard = [];
    foreach ($services as $s) {
        $keyboard[] = [[
            'text'          => "{$s['title']} — " . number_format($s['price'], 0, '', ' ') . ' ₽',
            'callback_data' => "service:{$s['id']}",
        ]];
    }
    $tg->sendMessage($chatId, "Выберите услугу:", $keyboard);
}

// Главный цикл
while (true) {
    $updates = $tg->getUpdates($offset);

    foreach ($updates as $update) {
        $offset = $update['update_id'] + 1;

        // Нажатие кнопки
        if (isset($update['callback_query'])) {
            $cb     = $update['callback_query'];
            $chatId = $cb['message']['chat']['id'];
            $data   = $cb['data'];
            $tg->answerCallback($cb['id']);

            if (str_starts_with($data, 'service:')) {
                $serviceId = (int) explode(':', $data)[1];
                setSession($chatId, 'wait_name', ['service_id' => $serviceId]);
                $tg->sendMessage($chatId, "Как вас зовут?");
            }
            continue;
        }

        // Текстовое сообщение
        if (!isset($update['message']['text'])) continue;

        $chatId  = $update['message']['chat']['id'];
        $text    = trim($update['message']['text']);
        $session = getSession($chatId);

        // Команды
        if ($text === '/start') {
            setSession($chatId, 'idle');
            $tg->sendMessage($chatId, "Привет! Я помогу оформить заказ.");
            showServices($tg, $chatId);
            continue;
        }

        if ($text === '/services') {
            showServices($tg, $chatId);
            continue;
        }

        // Диалог — ждём имя
        if ($session['state'] === 'wait_name') {
            setSession($chatId, 'wait_email', array_merge($session['data'], ['name' => $text]));
            $tg->sendMessage($chatId, "Ваш email:");
            continue;
        }

        // Диалог — ждём email
        if ($session['state'] === 'wait_email') {
            $name      = $session['data']['name'];
            $serviceId = $session['data']['service_id'];
            $email     = $text;

            if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
                $tg->sendMessage($chatId, "Похоже это не email. Попробуйте ещё раз:");
                continue;
            }

            Order::create($serviceId, $name, $email);
            setSession($chatId, 'idle');

            $tg->sendMessage($chatId, "✅ Заявка принята, {$name}! Свяжемся с вами в ближайшее время.");

            // Уведомление админу
            $service = Service::findBySlug('');
            $tg->sendMessage($adminId,
                "🔔 <b>Новый заказ</b>\n" .
                "Услуга ID: {$serviceId}\n" .
                "Имя: {$name}\n" .
                "Email: {$email}"
            );
            continue;
        }

        // Непонятное сообщение
        $tg->sendMessage($chatId, "Напишите /start чтобы начать.");
    }

    if (empty($updates)) usleep(500000); // 0.5 сек пауза если нет обновлений
}