from dataclasses import dataclass
from dotenv import load_dotenv
import os

load_dotenv()

base_url_group = os.environ['base_url_group']


@dataclass
class ConfigVK:
    token = os.environ['token']
    group_id = os.environ['group_id']
    

@dataclass
class ConfigTG:
    token = os.environ['token_tg']
    group_id = os.environ['group_id_tg']

config_vk = ConfigVK()
config_tg = ConfigTG()
