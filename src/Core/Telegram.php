<?php
class Telegram {
    private string $token;
    private string $apiUrl;

    public function __construct(string $token) {
        $this->token  = $token;
        $this->apiUrl = "https://api.telegram.org/bot{$token}";
    }

    public function getUpdates(int $offset = 0): array {
        $url  = "{$this->apiUrl}/getUpdates?offset={$offset}&timeout=25";
        $data = json_decode(file_get_contents($url), true);
        return $data['result'] ?? [];
    }

    public function sendMessage(int $chatId, string $text, array $keyboard = []): void {
        $params = [
            'chat_id'    => $chatId,
            'text'       => $text,
            'parse_mode' => 'HTML',
        ];

        if ($keyboard) {
            $params['reply_markup'] = json_encode([
                'inline_keyboard' => $keyboard
            ]);
        }

        $this->post('sendMessage', $params);
    }

    public function answerCallback(string $callbackId): void {
        $this->post('answerCallbackQuery', ['callback_query_id' => $callbackId]);
    }

    private function post(string $method, array $params): void {
        $ctx = stream_context_create(['http' => [
            'method'  => 'POST',
            'header'  => 'Content-Type: application/json',
            'content' => json_encode($params),
        ]]);
        file_get_contents("{$this->apiUrl}/{$method}", false, $ctx);
    }
}