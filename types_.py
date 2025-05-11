from abc import abstractmethod
from enum import EnumMeta
import os
from pydantic import BaseModel


class TypeMedia(EnumMeta):
    """
    Перечисление для типов медиа.

    Attributes:
        photo (str): Тип медиа - фото.
        video (str): Тип медиа - видео.
    """

    photo = "photo"
    video = "video"


class URLMedia(BaseModel):
    """
    Класс для хранения URL медиа.

    Attributes:
        url (str): URL медиа.
        type (str): Тип медиа.
    """

    url: str
    type: str


class File(BaseModel):
    path: str
    type: str
    
    def delete(self):
        os.remove(self.path)


class Text(BaseModel):
    """
    Класс для хранения текста поста.

    Attributes:
        original (str): Оригинальный текст поста.
        first (str): Текст, который будет добавлен перед оригинальным текстом.
        last (str): Текст, который будет добавлен после оригинального текста.

    Properties:
        text (str): Полный текст поста, состоящий из first, original и last.
    """

    original: str = ""
    first: str = ""
    last: str = ""

    @property
    def text(self):
        return self.first + self.original + self.last


class Post(BaseModel):
    """
    Класс для хранения поста.

    Attributes:
        text (Text): Объект текста поста.
        media_urls (list[URLMedia]): Список URL медиа, связанных с постом.
        media_files (list[File]): Список скаченных файлов
    """

    text: Text
    media_urls: list[URLMedia] = []
    media_files: list[File] = []


class Bot:
    """
    Абстрактный базовый класс для бота.

    Methods:
        send_message(post): Абстрактный метод для отправки сообщения.
    """

    @abstractmethod
    def send_message(self, post):
        """
        Отправка сообщения.

        :param post: Объект поста, содержащий текст и медиа.
        """
        ...


class ReplaceTemplate(BaseModel):
    template: str
    replace_to: str
