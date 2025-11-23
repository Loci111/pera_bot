import os
import time
import sys
import threading

import telebot

from utils import setup_logging, load_json_data
from handlers import register_handlers
from config import TELEGRAM_BOT_API_TOKEN, GROUP_CHAT_ID, DB_CONFIG
from db import Database


def create_bot():
    data_directory = "./data"
    if not os.path.exists(data_directory):
        os.makedirs(data_directory)

    logger = setup_logging(data_directory)

    try:
        bot_instance = telebot.TeleBot(TELEGRAM_BOT_API_TOKEN)
        logger.info("Бот успешно инициализирован.")
    except Exception:
        logger.error("Ошибка при инициализации бота", exc_info=True)
        raise

    db = Database(DB_CONFIG, logger)

    data = {
        'users_info': {},
        'pre_signup_info': {},
        'pre_signup_a1_n5_info': {},
        'unique_visits': set(),
        'message_user_map': {},
        'GROUP_CHAT_ID': GROUP_CHAT_ID,
        'materials': [{
            "id": "love_guide",
            "name": "Скачать гайд про любовь",
            "description": "Полезный гайд про любовь.",
            "file_path": os.path.join(data_directory, "guide_love.pdf")
        }],
        'messages': load_json_data('messages.json', {}),
        'logger': logger,
        'db': db,
    }

    register_handlers(bot_instance, data)
    logger.info("Обработчики успешно зарегистрированы.")

    return bot_instance, logger


def main():
    try:
        bot_instance, logger = create_bot()
    except Exception:
        sys.exit(1)

    def thread_exception_handler(args):
        logger.error("Необработанное исключение в потоке", exc_info=(args.exc_type, args.exc_value, args.exc_traceback))

    if sys.version_info >= (3, 8):
        threading.excepthook = thread_exception_handler

    logger.info("Бот запущен и готов к работе.")
    while True:
        try:
            bot_instance.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e:
            logger.error(f"Ошибка в работе бота: {e}", exc_info=True)
            time.sleep(5)


if __name__ == "__main__":
    main()

