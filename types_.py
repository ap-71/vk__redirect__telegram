from abc import abstractmethod
from dataclasses import dataclass
from enum import EnumMeta


class TypeMedia(EnumMeta):
    photo = 'photo'
    video = 'video'


@dataclass
class URLMedia:
    url: str
    type: str


@dataclass
class Text:
    original: str = ''
    first: str = ''
    last: str = ''
    
    @property
    def text(self):
        return self.first+self.original+self.last


@dataclass
class Post:
    text: Text
    media_urls: list[URLMedia] = tuple()


class Bot:
    @abstractmethod
    def send_message(self, post): ...
