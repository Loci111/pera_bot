print("[utils] started")
import os
print("[utils] cwd =", os.getcwd())
import json
import logging
from logging.handlers import TimedRotatingFileHandler
import re


def setup_logging(data_directory):
    # Создаем логгер с именем 'bot_logger'
    logger = logging.getLogger('bot_logger')
    logger.setLevel(logging.INFO)

    # Очищаем существующие обработчики, если они есть
    if logger.hasHandlers():
        logger.handlers.clear()

    # Создаем директорию для логов, если ее нет
    if not os.path.exists(data_directory):
        os.makedirs(data_directory)

    # Базовое имя лог-файла
    log_filename = os.path.join(data_directory, 'bot.log')

    # Настраиваем TimedRotatingFileHandler с ротацией в полночь
    file_handler = TimedRotatingFileHandler(
        filename=log_filename,
        when='midnight',
        interval=1,
        backupCount=7,
        encoding='utf-8'
    )

    # Добавляем суффикс с датой к имени файла
    file_handler.suffix = "%d.%m.%Y"

    # Устанавливаем соответствие между суффиксами файлов
    file_handler.extMatch = re.compile(r"^\\d{2}\\.\\d{2}\\.\\d{4}$")

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Добавляем обработчик файла в логгер
    logger.addHandler(file_handler)

    # Настраиваем консольный обработчик
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger  # Возвращаем настроенный логгер


def send_error_message(bot, chat_id, error_message):
    bot.send_message(chat_id, f"Ошибка: {error_message}")


def load_json_data(file_path, default_data):
    """Загружает данные из JSON файла"""
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return default_data


def save_json_data(file_path, data):
    """Сохраняет данные в JSON файл"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

