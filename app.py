import os
import time
import loguru
from config import MEDIA_SAVE_TO, config_tg, config_vk
from base import TG, VKRedirectTo


def main():
    """
    Основная функция для запуска перенаправления постов из VK в Telegram.

    Эта функция инициализирует объект VKRedirectTo и запускает его метод run(),
    который обрабатывает посты из VK и перенаправляет их в Telegram.
    В случае ошибки функция повторяет попытку до достижения максимального количества попыток.
    """
    retries = 0
    max_retries = 5
    time_sleep_sec = 15

    loguru.logger.info("Запуск")
    os.makedirs(MEDIA_SAVE_TO, exist_ok=True)

    while retries < max_retries:
        try:
            vk_redirect_tg = VKRedirectTo(
                group_api_token=config_vk.token,
                group_id=config_vk.group_id,
                redirect_to=TG(token=config_tg.token, group_id=config_tg.group_id),
            )
            vk_redirect_tg.run()
        except Exception as e:
            loguru.logger.error(f"Ошибка: {e}")
            retries += 1
            if retries < max_retries:
                loguru.logger.info(f"Повтор {retries} из {max_retries}")
                time.sleep(time_sleep_sec)

    loguru.logger.info("Работа завершена")


if __name__ == "__main__":
    main()
