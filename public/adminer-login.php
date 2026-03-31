<?php
function adminer_object() {
    class AdminerSoftware extends Adminer {
        function login($login, $password) {
            return true; // дозволяємо вхід без пароля
        }
    }
    return new AdminerSoftware;
}

include './adminer.php';