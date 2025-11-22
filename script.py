import telebot
import os
import logging
import time
import sys
import threading
from logging.handlers import TimedRotatingFileHandler
from utils import setup_logging, load_users_info, load_json_data
from handlers import register_handlers
from config import TELEGRAM_BOT_API_TOKEN, GROUP_CHAT_ID

# Настройка директорий и файлов данных
data_directory = "./data"
if not os.path.exists(data_directory):
    os.makedirs(data_directory)

# Настраиваем логирование и получаем логгер
logger = setup_logging(data_directory)

# Инициализация бота
try:
    bot = telebot.TeleBot(TELEGRAM_BOT_API_TOKEN)
    logger.info("Бот успешно инициализирован.")
except Exception as e:
    logger.error("Ошибка при инициализации бота", exc_info=True)
    sys.exit(1)

# Глобальные данные
data = {}
data['users_info'] = {}
data['pre_signup_info'] = {}
data['pre_signup_a1_n5_info'] = {}    # Для A1–N5
data['unique_visits'] = set()  # Для подсчета уникальных пользователей
data['message_user_map'] = {}
data['GROUP_CHAT_ID'] = GROUP_CHAT_ID
data['analytics_file'] = os.path.join(data_directory, "analytics.json")
data['analytics_data'] = load_json_data(data['analytics_file'], {"website_clicks": 0})
data['materials'] = [{
    "id": "love_guide",
    "name": "Скачать гайд про любовь",
    "description": "Полезный гайд про любовь.",
    "file_path": os.path.join(data_directory, "guide_love.pdf")
}]
data['messages'] = load_json_data('messages.json', {})
data['excel_file'] = os.path.join(data_directory, "users_info.xlsx")
data['pre_signup_file'] = os.path.join(data_directory, "pre_signup_info.xlsx")
data['start_users_file'] = os.path.join(data_directory, "start_users.xlsx")
data['pre_signup_a1_n5_file'] = os.path.join(data_directory, "pre_signup_a1_n5.xlsx")  # <--- Новый путь
data['logger'] = logger  # Передаем логгер в data

# Загрузка информации о пользователях
data['users_info'] = load_users_info(data['excel_file'], logger)
data['pre_signup_info'] = load_users_info(data['pre_signup_file'], logger)
data['pre_signup_a1_n5_info'] = load_users_info(data['pre_signup_a1_n5_file'], logger)   # <--- Новая таблица

# Регистрация обработчиков
try:
    register_handlers(bot, data)
    logger.info("Обработчики успешно зарегистрированы.")
except Exception as e:
    logger.error("Ошибка при регистрации обработчиков", exc_info=True)
    sys.exit(1)

# Глобальный обработчик исключений для потоков (Python 3.8+)
def thread_exception_handler(args):
    logger.error("Необработанное исключение в потоке", exc_info=(args.exc_type, args.exc_value, args.exc_traceback))

if sys.version_info >= (3, 8):
    threading.excepthook = thread_exception_handler

# Используем infinity_polling для автоматического перезапуска при сбоях
if __name__ == "__main__":
    logger.info("Бот запущен и готов к работе.")
    while True:
        try:
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e:
            logger.error(f"Ошибка в работе бота: {e}", exc_info=True)
            time.sleep(5)  # Ждем 5 секунд перед новой попыткой
