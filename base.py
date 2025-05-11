import re
from typing import List
import loguru
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEvent
import telebot
from telebot.types import InputMediaPhoto, InputMediaVideo, InputFile
import yt_dlp
from helpers import GetFileName
from types_ import Bot, File, Post, ReplaceTemplate, Text, TypeMedia, URLMedia
from config import MAX_TEXT_LENGTH, MEDIA_SAVE_TO, config_vk


class TG(Bot):
    """
    Класс для работы с Telegram ботом.
    """

    def __init__(self, token: str, group_id: int, parse_mode: str = "HTML") -> None:
        """
        Инициализация бота Telegram.

        :param token: Токен для доступа к Telegram API.
        :param group_id: ID группы, в которую будут отправляться сообщения.
        :param parse_mode: Режим разметки сообщений (по умолчанию "HTML").
        """
        self._bot = telebot.TeleBot(token=token, parse_mode=parse_mode)
        self._group_id = group_id

    def send_message(self, post: Post) -> None:
        """
        Отправка сообщения в группу Telegram.

        :param post: Объект поста, содержащий текст и медиа.
        """
        text = post.text
        if len(text.original) > MAX_TEXT_LENGTH:
            text.original = text.original[:MAX_TEXT_LENGTH] + "..."

        if not post.media_urls and not post.media_files:
            self._bot.send_message(
                chat_id=self._group_id, text=text.text, disable_web_page_preview=True
            )
        else:
            medias = []
            text_add = False
            
            imv = None
            for i, mu in enumerate(post.media_urls):
                if mu.type == TypeMedia.photo:
                    media=mu.url
                    caption=text.text if i == 0 else None
                    
                    imv = InputMediaPhoto(media=media, caption=caption)
                elif mu.type == TypeMedia.video:
                    media=mu.url
                    caption=text.text if i == 0 else None
                    
                    imv = InputMediaVideo(media=media, caption=caption)
                
                if imv:
                    medias.append(imv)
                    text_add = True

            imv = None
            for i, mu in enumerate(post.media_files):
                if mu.type == TypeMedia.video:
                    media=InputFile(mu.path)
                    caption = text.text if i == 0 and not text_add else None
                    
                    imv = InputMediaVideo(media=media, caption=caption)
                    
                if imv:
                    medias.append(imv)
                    text_add = True

            self._bot.send_media_group(chat_id=self._group_id, media=medias)


class VKRedirectTo:
    """
    Класс для перенаправления постов из VK в Telegram.
    """

    def __init__(
        self,
        group_api_token: str,
        group_id: int,
        redirect_to: Bot,
        pooling_wait: int = 25,
        base_url_group: str = config_vk.url_group_base,
        clean_text_templates: List[ReplaceTemplate] | None = None,
    ) -> None:
        """
        Инициализация перенаправления постов.

        :param group_api_token: Токен для доступа к VK API.
        :param group_id: ID группы VK.
        :param redirect_to: Объект бота Telegram, в который будут перенаправляться посты.
        :param pooling_wait: Время ожидания между запросами к VK API.
        :param base_url_group: Базовый URL группы VK.
        :param clean_text_templates: шаблоны для очистки в формате [["здесь_шаблон", "то_на_что_меняем"]]
        """
        self._clean_text_templates: List[ReplaceTemplate] = []
        if clean_text_templates is None:
            self._clean_text_templates = [
                ReplaceTemplate(template="^источник.*http.*", replace_to="")
            ]
        else:
            self._clean_text_templates = clean_text_templates

        self._vk_session = vk_api.VkApi(token=group_api_token)
        self._vk_bot = VkBotLongPoll(self._vk_session, group_id, wait=pooling_wait)
        self._bot_to = redirect_to
        self._base_url_group = base_url_group

    def _clean_text(self, text: str | None = None) -> str:
        if text is None:
            text = ""

            return text

        text_ = text

        for rt in self._clean_text_templates:
            text_ = re.sub(rt.template, rt.replace_to, text_, flags=re.IGNORECASE)

        return text_

    def _get_video(self, owner_id, video_id, url=config_vk.url_video) -> File | None:
        """
        Получение видео

        :param owner_id: id_владельца_видео
        :param video_id: id_видео
        """
        try:
            get_file_name = GetFileName()

            ydl_opts = {
                "outtmpl": MEDIA_SAVE_TO+"/%(title)s.%(ext)s",
                "progress_hooks": [get_file_name.hook],
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url.format(video_owner_id=owner_id, video_id=video_id)])

            return File(path=get_file_name.file_name, type=TypeMedia.video)
        except Exception as e:
            loguru.logger.error(f"Ошибка при скачивании видео: {e}")

    def _process_attachment(self, att: dict) -> URLMedia | File | None:
        type_ = att.get("type")

        if not type_:
            return None

        try:
            if type_ == "video":
                video = att[type_]

                file: File | None = self._get_video(
                    owner_id=video["owner_id"], video_id=video["id"]
                )

                return file
            else:
                return URLMedia(url=att[type_]["orig_" + type_]["url"], type=type_)
        except KeyError as e:
            loguru.logger.error(f"KeyError processing attachment: {str(e)}")
            images = att[type_].get("image", [])
            if images:
                url = max(images, key=lambda img: img.get("width", 0)).get("url")
                if url:
                    return URLMedia(url=url, type=TypeMedia.photo)
        except Exception as e:
            loguru.logger.error(f"Unexpected error processing attachment: {str(e)}")

    def get_posts(self, data: VkBotEvent) -> list[Post]:
        posts = []

        new_posts = data.object.get("copy_history", [data.object])

        for ch in new_posts:
            urls_media = []
            media_files = []
            source_id = ch.get("owner_id")

            text_raw = ch.get("text", "")
            text_raw = self._clean_text(text_raw)

            text = Text(original=text_raw)

            if ch.get("post_type") == "suggest":
                loguru.logger.info(
                    f"Skipping post with type 'suggest': {ch.get('text')}"
                )
                continue

            if text.original and source_id is not None:
                full_path_source = f"{self._base_url_group}{abs(source_id)}"
                text.last = f'\n\n<a href="{full_path_source}">Источник</a>'

            i = 0
            for att in ch.get("attachments", []):
                i += 1
                
                media = self._process_attachment(att)

                if isinstance(media, URLMedia):
                    urls_media.append(media)
                elif isinstance(media, File):
                    media_files.append(media)

            if (i > 0 and (len(urls_media) > 0 or len(media_files) > 0)) or i == 0:
                posts.append(
                    Post(text=text, media_urls=urls_media, media_files=media_files)
                )
            else:
                loguru.logger.info("Пост пропущен. Вложения есть, но их не получилось скачать.")

        return posts

    def _repost_to(self, posts: List[Post]):
        for post in posts:
            try:
                self._bot_to.send_message(post=post)
            except Exception as e:
                loguru.logger.error(f"Ошибка при отправки сообщения в телеграм: {e}")
    
    def _delete_media_from_server(self, files: List[File]):
        for file in files:
            try:
                file.delete()
            except Exception as e:
                loguru.logger.error(f"Ошибка при удалении файла: {e}")
            
    def run(self) -> None:
        for data in self._vk_bot.listen():
            try:
                posts = self.get_posts(data=data)
            except Exception as e:
                loguru.logger.error(f"Error processing data: {str(e)}")
                continue

            self._repost_to(posts)
            
            files: List[File] = []
            for post in posts:
                files += post.media_files
                
            self._delete_media_from_server(files)