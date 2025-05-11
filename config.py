from dataclasses import dataclass
from dotenv import load_dotenv
import os

from pydantic import BaseModel

# Загрузка переменных окружения из файла .env
load_dotenv()

MAX_TEXT_LENGTH = 3800
MEDIA_SAVE_TO = 'media'

class ConfigVK(BaseModel):
    """
    Конфигурация для VK.

    Attributes:
        token (str): Токен для доступа к VK API.
        group_id (int): ID группы VK.
    """

    token: str = os.environ["token"]
    group_id: int = int(os.environ["group_id"])
    url_group_base: str="https://vk.com/public"
    url_video: str="https://vk.com/video{video_owner_id}_{video_id}"


class ConfigTG(BaseModel):
    """
    Конфигурация для Telegram.

    Attributes:
        token (str): Токен для доступа к Telegram API.
        group_id (int): ID группы Telegram.
    """

    token: str = os.environ["token_tg"]
    group_id: int = int(os.environ["group_id_tg"])


# Создание экземпляров конфигураций
config_vk = ConfigVK()
config_tg = ConfigTG()
