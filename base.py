import loguru
from config import base_url_group
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll
import telebot
from telebot.types import InputMediaPhoto, InputMediaVideo
from types_ import Bot, Post, Text, TypeMedia, URLMedia


class TG(Bot):
    def __init__(self, token, group_id, parse_mode='HTML') -> None:
        self._bot = telebot.TeleBot(token=token, parse_mode=parse_mode)
        self._group_id = group_id
    
    def send_message(self, post: Post):
        text: Text = post.text
        
        if text.original.__len__() > 3800:
            text.original = text.original[0:3800]
            text.original += '...'
            
        if post.media_urls.__len__() == 0:
            self._bot.send_message(
                chat_id=self._group_id, 
                text=text.text, 
                disable_web_page_preview=True
            )
        else:
            medias = []
            
            for i, mu in enumerate(post.media_urls):
                type_ = mu.type
                media_url = mu.url
                media = None
                caption = text.text if i == 0 else None
                
                if type_ == TypeMedia.photo:
                    media = InputMediaPhoto(media=media_url, caption=caption)
                elif type_ == TypeMedia.video:
                    media = InputMediaVideo(media=media_url, caption=caption)
                    
                if media is not None:
                    medias.append(media)
            
            self._bot.send_media_group(chat_id=self._group_id, media=medias)


class VKRedirectTo:
    def __init__(
        self, 
        group_api_token, 
        group_id, 
        redirect_to: Bot, 
        pooling_wait=25, 
        base_url_group=base_url_group
    ) -> None:
        self._vk_session = vk_session = vk_api.VkApi(token=group_api_token)
        self._vk_bot = VkBotLongPoll(vk_session, group_id, wait=pooling_wait)
        self._bot_to = redirect_to
        self._base_url_group = base_url_group

    def get_posts(self, data) -> list[Post]:
        posts: list[Post] = []
        new_posts = data.object.get('copy_history')
        
        if new_posts is None:
            new_posts = [data.object]

        for ch in new_posts:
            urls_media = []
            source_id = ch.get('owner_id')
            
            text = Text(
                original=ch.get('text')
            )
            
            if ch.get('post_type') == 'suggest':
                # пропускаем, если сообщение предложенное
                continue
            
            if text.original is not None and text.original != '' and source_id is not None:
                full_path_source = self._base_url_group+str(abs(source_id))
                text.last = f'\n\n<a href="{full_path_source}">Источник</a>'
                
            for att in ch['attachments']:
                type_ = att.get('type')
                
                if type_ is None:
                    continue
                
                try:
                    urls_media.append(URLMedia(url=att[type_]['orig_'+type_]['url'], type=type_))
                except KeyError as e:
                    images: list[dict] = att[type_].get('image', [])
                    width = 0
                    url = None
                    
                    for image in images:
                        url_ = image.get('url')
                        width_ = image.get('width', 0)
                        
                        if width_ > width:
                            width = width_
                            url = url_
                        elif width_ < width:
                            break
                    
                    if url is not None:
                        urls_media.append(URLMedia(url=url, type=TypeMedia.photo))
                except Exception as e:
                    print('error get media => ', str(e))
            
            # для отладки
            try:
                loguru.logger.info(ch)
            except Exception as e:
                pass
            
            posts.append(Post(text=text, media_urls=urls_media))
        
        return posts

    def run(self):
        for data in self._vk_bot.listen():
            try:
                posts = self.get_posts(data=data)
            except Exception as e:
                posts = []
            
            for post in posts:
                self._bot_to.send_message(post=post)
