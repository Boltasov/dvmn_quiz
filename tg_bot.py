import logging
import os
import redis

from functools import partial
from enum import Enum

from dotenv import load_dotenv
from telegram import Update, ForceReply, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler

from quiz import get_random_question, get_answer

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


class State(Enum):
    MENU = 1
    ANSWER = 2
    BLUE = 3


def start(update: Update, context: CallbackContext) -> State:
    """Send a message when the command /start is issued."""
    user = update.effective_user

    quiz_menu = [['Новый вопрос', 'Сдаться'],
                 ['Мой счёт']]
    reply_markup = ReplyKeyboardMarkup(quiz_menu)

    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=reply_markup,
    )

    return State.MENU


def handle_new_question_request(update: Update, context: CallbackContext, db_connection, quiz_dir) -> State:
    question_id, question, quiz_file = get_random_question(quiz_dir=quiz_dir)

    db_connection.set(update.message.chat_id, question_id)
    context.user_data['quiz_file'] = quiz_file

    update.message.reply_text(question)
    update.message.reply_text('Введите ваш ответ:')

    return State.ANSWER


def handle_solution_attempt(update: Update, context: CallbackContext, db_connection, quiz_dir) -> State:
    message = update.message.text

    question_id = int(db_connection.get(update.message.chat_id))
    right_answer = get_answer(question_id, context.user_data['quiz_file'], quiz_dir=quiz_dir)

    if message == right_answer:
        result = 'Верно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»'
    else:
        result = 'Неверно. Попробуешь ещё раз?'

    quiz_menu = [['Новый вопрос', 'Сдаться'],
                 ['Мой счёт']]
    reply_markup = ReplyKeyboardMarkup(quiz_menu)

    response = f'{result}\n\nПравильный ответ: {right_answer}\nВаш ответ: {message}'

    update.message.reply_text(response, reply_markup=reply_markup)

    return State.MENU


def handle_give_up(update: Update, context: CallbackContext, db_connection, quiz_dir) -> State:
    question_id = int(db_connection.get(update.message.chat_id))

    right_answer = get_answer(question_id, context.user_data['quiz_file'], quiz_dir)

    question_id, question, quiz_file = get_random_question(quiz_dir=quiz_dir)
    context.user_data['quiz_file'] = quiz_file
    db_connection.set(update.message.chat_id, question_id)

    update.message.reply_text(f'Правильный ответ: {right_answer}')
    update.message.reply_text(f'Следующий вопрос: {question}')
    update.message.reply_text(f'Введите ваш ответ')

    return State.ANSWER


if __name__ == "__main__":
    """Start the bot."""
    load_dotenv()

    # connect to db
    redis_host = os.getenv('REDIS_HOST')
    redis_port = os.getenv('REDIS_PORT')
    redis_username = os.getenv('REDIS_USERNAME')
    redis_password = os.getenv('REDIS_PASSWORD')
    db_connection = redis.Redis(host=redis_host, port=redis_port, username=redis_username, password=redis_password,
                                decode_responses=True)

    tg_token = os.getenv('TG_TOKEN')
    updater = Updater(tg_token)

    dispatcher = updater.dispatcher

    quiz_dir = os.getenv('QUIZ_DIR')
    handle_new_question_request_db = partial(handle_new_question_request,
                                             db_connection=db_connection,
                                             quiz_dir=quiz_dir)
    handle_solution_attempt_db = partial(handle_solution_attempt,
                                         db_connection=db_connection,
                                         quiz_dir=quiz_dir)
    handle_give_up_db = partial(handle_give_up,
                                db_connection=db_connection,
                                quiz_dir=quiz_dir)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            State.MENU: [MessageHandler(Filters.text('Новый вопрос'), handle_new_question_request_db)],
            State.ANSWER: [MessageHandler(Filters.text('Сдаться'), handle_give_up_db),
                           MessageHandler(Filters.text, handle_solution_attempt_db)],
        },
        fallbacks=[]
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()
