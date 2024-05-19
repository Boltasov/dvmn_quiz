import logging
import random
import os
import redis

from dotenv import load_dotenv
from enum import Enum

import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from quiz import get_random_question, get_answer


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


class State(Enum):
    MENU = 1
    ANSWER = 2
    UNDEFINED = 3


def get_keyboard():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.PRIMARY)

    keyboard.add_line()
    keyboard.add_button('Счёт', color=VkKeyboardColor.PRIMARY)

    return keyboard


def start(event, vk_api):
    keyboard = get_keyboard()

    reply = 'Привет! Это квиз-бот. Нажми кнопку "Новый вопрос"'

    vk_api.messages.send(
        user_id=event.user_id,
        message=reply,
        random_id=random.randint(1, 1000),
        keyboard=keyboard.get_keyboard(),
    )

    return State.MENU


def handle_new_question_request(event, vk_api, db_connection):
    question_id, question, quiz_file = get_random_question()

    db_connection.set(event.user_id, question_id)

    keyboard = get_keyboard()

    vk_api.messages.send(
        user_id=event.user_id,
        message=question,
        random_id=random.randint(1, 1000),
    )
    vk_api.messages.send(
        user_id=event.user_id,
        message='Введите ваш ответ:',
        random_id=random.randint(1, 1000),
        keyboard=keyboard.get_keyboard(),
    )

    return State.ANSWER, quiz_file


def handle_give_up(event, vk_api, db_connection, quiz_file):
    question_id = int(db_connection.get(event.user_id))

    right_answer = get_answer(question_id, quiz_file)

    question_id, question, quiz_file = get_random_question()
    db_connection.set(event.user_id, question_id)

    keyboard = get_keyboard()

    vk_api.messages.send(
        user_id=event.user_id,
        message=f'Правильный ответ: {right_answer}',
        random_id=random.randint(1, 1000),
    )
    vk_api.messages.send(
        user_id=event.user_id,
        message=f'Следующий вопрос: {question}',
        random_id=random.randint(1, 1000),
    )
    vk_api.messages.send(
        user_id=event.user_id,
        message=f'Введите ваш ответ',
        random_id=random.randint(1, 1000),
        keyboard=keyboard.get_keyboard(),
    )

    return State.ANSWER, quiz_file


def handle_solution_attempt(event, vk_api, db_connection, quiz_file):
    message = event.text

    question_id = int(db_connection.get(event.user_id))
    right_answer = get_answer(question_id, quiz_file)

    if message == right_answer:
        result = 'Верно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»'
    else:
        result = 'Неверно. Попробуешь ещё раз?'

    keyboard = get_keyboard()

    response = f'{result}\n\nПравильный ответ: {right_answer}\nВаш ответ: {message}'

    vk_api.messages.send(
        user_id=event.user_id,
        message=response,
        random_id=random.randint(1, 1000),
        keyboard=keyboard.get_keyboard(),
    )

    return State.MENU


if __name__ == "__main__":
    """Start the bot."""
    load_dotenv()

    redis_host = os.getenv('REDIS_HOST')
    redis_port = os.getenv('REDIS_PORT')
    redis_username = os.getenv('REDIS_USERNAME')
    redis_password = os.getenv('REDIS_PASSWORD')
    db_connection = redis.Redis(host=redis_host, port=redis_port, username=redis_username, password=redis_password,
                                decode_responses=True)

    state = State.UNDEFINED

    vk_token = os.getenv('VK_ACCESS_TOKEN')
    vk_session = vk.VkApi(token=vk_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:

            match state:
                case State.UNDEFINED:
                    state = start(event, vk_api)
                    continue
                case State.MENU:
                    if event.message == 'Новый вопрос':
                        state, quiz_file = handle_new_question_request(event, vk_api, db_connection)
                        continue
                    else:
                        continue
                case State.ANSWER:
                    if event.text == 'Сдаться':
                        state, quiz_file = handle_give_up(event, vk_api, db_connection, quiz_file)
                        continue
                    else:
                        state = handle_solution_attempt(event, vk_api, db_connection, quiz_file)
                        continue

