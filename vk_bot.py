import logging
import random
import os
import redis

from dotenv import load_dotenv

import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType

from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def start(event, vk_api):
    keyboard = VkKeyboard(one_time=True)

    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.PRIMARY)

    keyboard.add_line()
    keyboard.add_button('Счёт', color=VkKeyboardColor.PRIMARY)

    vk_api.messages.send(
        user_id=event.user_id,
        message=event.text,
        random_id=random.randint(1, 1000),
        keyboard=keyboard.get_keyboard(),
    )


if __name__ == "__main__":
    load_dotenv()
    redis_host = os.getenv('REDIS_HOST')
    redis_port = os.getenv('REDIS_PORT')
    redis_username = os.getenv('REDIS_USERNAME')
    redis_password = os.getenv('REDIS_PASSWORD')
    db_connection = redis.Redis(host=redis_host, port=redis_port, username=redis_username, password=redis_password,
                                decode_responses=True)
    vk_token = os.getenv('VK_ACCESS_TOKEN')

    vk_session = vk.VkApi(token=vk_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if event.text == 'Новый вопрос':
                pass
            elif event.text == 'Сдаться':
                pass
            elif event.text == 'Мой счёт':
                pass
            else:
                start(event, vk_api)
