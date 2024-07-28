import time
import loguru
from config import config_tg, config_vk
from base import TG, VKRedirectTo


retries = 0
max_retries = 5
time_sleep_sec = 15

loguru.logger.info('Запуск')

while True:
    try:
        vk_redirect_tg = VKRedirectTo(
            group_api_token=config_vk.token, 
            group_id=config_vk.group_id,
            redirect_to=TG(
                token=config_tg.token, 
                group_id=config_tg.group_id
            )
        )
        vk_redirect_tg.run()
    except Exception as e:
        loguru.logger.error('Ошибка: '+str(e))
        retries += 1
        if retries < max_retries:
            loguru.logger.info(f'Повтор {retries} из {max_retries}')
            time.sleep(time_sleep_sec)
            continue
        else:
            break

loguru.logger.info('Работа завершена')
