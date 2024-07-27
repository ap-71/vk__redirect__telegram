import os
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll
import telebot
from telebot.types import InputMediaPhoto


token = os.environ['token']
token_tg = os.environ['token_tg']
group_id = os.environ['group_id']
group_id_tg = os.environ['group_id_tg']
base_url_group = os.environ['base_url_group']

vk_session = vk_api.VkApi(token=token)

bot = VkBotLongPoll(vk_session, group_id, wait=25)
bot_tg = telebot.TeleBot(token_tg, parse_mode='HTML')


def get_copy_history(data):
    posts = []
    
    for ch in data.object.get('copy_history', []):
        source_id = ch.get('owner_id')
        
        text = ch.get('text')
        
        if text is not None and text != '' and source_id is not None:
            full_path_source = base_url_group+str(abs(source_id))
            text += f'\n\n<a href="{full_path_source}">Источник</a>'
        else:
            text = ''
            
        for att in ch['attachments']:
            type_ = att.get('type')
            
            if type_ is None:
                continue
            
            try:
                urls_media.append(dict(url=att[type_]['orig_'+type_]['url'], type=type_))
            except Exception as e:
                print('error get media => ', str(e))
        posts.append({ "text": text, "media_urls": urls_media})
    
    return posts


for data in bot.listen():
    urls_media = []
    full_path_source = None
    
    try:
        posts = get_copy_history(data=data)
    except Exception as e:
        posts = []
    
    for post in posts:
        text = post['text']
        media_urls = post['media_urls']
        
        if media_urls.__len__() == 0:
            bot_tg.send_message(chat_id=group_id_tg, text=text)
        else:
            medias = []
            
            for i, mu in enumerate(media_urls):
                type_ = mu['type']
                media_url = mu['url']
                media = None
                
                if type_ == 'photo':
                    media = InputMediaPhoto(media=media_url, caption=text if i == 0 else None)
                
                if media is not None:
                    medias.append(media)
            
            bot_tg.send_media_group(chat_id=group_id_tg, media=medias)
