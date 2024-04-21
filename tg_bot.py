import logging
from functools import partial
from enum import Enum

import redis
from telegram import Update, ForceReply, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler

from main import get_quiz, get_random_question, get_answer

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


# class syntax
class State(Enum):
    MENU = 1
    ANSWER = 2
    BLUE = 3


def start(update: Update, context: CallbackContext) -> None:
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


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def handle_new_question_request(update: Update, context: CallbackContext, db_connection) -> None:
    message = update.message.text
    if message == 'Новый вопрос':
        question_id, question = get_random_question()

    db_connection.set(update.message.chat_id, question_id)

    update.message.reply_text(question)
    update.message.reply_text('Введите ваш ответ:')

    return State.ANSWER


def handle_solution_attempt(update: Update, context: CallbackContext, db_connection) -> None:
    message = update.message.text

    question_id = int(db_connection.get(update.message.chat_id))
    right_answer = get_answer(question_id)

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


def handle_give_up(update: Update, context: CallbackContext, db_connection) -> None:
    question_id = int(db_connection.get(update.message.chat_id))

    right_answer = get_answer(question_id)

    question_id, question = get_random_question()
    db_connection.set(update.message.chat_id, question_id)

    update.message.reply_text(f'Правильный ответ: {right_answer}')
    update.message.reply_text(f'Следующий вопрос: {question}')
    update.message.reply_text(f'Введите ваш ответ')

    return State.ANSWER


def main() -> None:
    """Start the bot."""
    # connect to db
    db_connection = redis.Redis(host='redis-17198.c74.us-east-1-4.ec2.cloud.redislabs.com', port=17198, username='default', password='ooQSxegPkdQwVILzMXLBrctzenDcAyo1',
                                  decode_responses=True)
    print(db_connection.ping())

    # Create the Updater and pass it your bot's token.
    updater = Updater("6230042552:AAHJEdU6zGsIywKH-AYJxfDGHKRKsTi3vZo")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    #dispatcher.add_handler(CommandHandler("start", start))
    #dispatcher.add_handler(CommandHandler("help", help_command))

    handle_new_question_request_db = partial(handle_new_question_request, db_connection=db_connection)
    handle_solution_attempt_db = partial(handle_solution_attempt, db_connection=db_connection)
    handle_give_up_db = partial(handle_give_up, db_connection=db_connection)

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


if __name__ == '__main__':
    main()
