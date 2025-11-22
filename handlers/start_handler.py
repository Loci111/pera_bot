from telebot import types
from utils import send_error_message, save_to_excel

def register_start_handlers(bot, data):
    messages = data['messages']
    users_info = data['users_info']
    GROUP_CHAT_ID = data['GROUP_CHAT_ID']
    start_users_file = data['start_users_file']
    logger = data['logger']

    # Флаг показа кнопки "Марафон по японским азбукам"
    SHOW_AZBUKA_MARATHON_BUTTON = True  # временно скрываем

    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        try:
            chat_id = message.chat.id
            user_id = message.from_user.id
            username = message.from_user.username if message.from_user.username else "Нет никнейма"

            users_info[user_id] = {
                'chat_id': chat_id,
                'username': username
            }

            logger.info(f"Пользователь @{username} (ID: {user_id}) нажал /start.")

            user_info = {
                'chat_id': user_id,
                'username': username
            }

            save_to_excel(user_info, filename=start_users_file, logger=logger)

            bot.send_photo(chat_id, open('page_start.jpg', 'rb'))
            bot.send_message(chat_id, messages['welcome_text'], parse_mode='Markdown')

            markup = types.InlineKeyboardMarkup()

            # --- КНОПКИ ГЛАВНОГО МЕНЮ ---

            # (СКРЫТА) Марафон по японским азбукам — функционал не удаляем, только кнопку не показываем
            if SHOW_AZBUKA_MARATHON_BUTTON:
                markup.add(types.InlineKeyboardButton('Марафон по японским азбукам', callback_data='marathon'))

            # Новая кнопка: Марафон по кандзи — прямая ссылка на курс
            markup.add(types.InlineKeyboardButton('Марафон по кандзи', url='https://peraperajapanese.tilda.ws/200kanji'))

            # Курс А1 (как было)
            markup.add(types.InlineKeyboardButton('Японский для новичков от А0 до А1', callback_data='a1'))

            # Если ты уже добавлял вкладку A1–N5 — оставляем её здесь
            # (если не нужно — можешь удалить следующую строку)
            markup.add(types.InlineKeyboardButton('Японский от А1 до N5', callback_data='a1_n5'))

            # Остальные кнопки
            markup.add(types.InlineKeyboardButton('Скачать полезные материалы', callback_data='download_materials'))
            markup.add(types.InlineKeyboardButton('Перейти на сайт', url='https://peraperajapanese.tilda.ws/'))
            markup.add(types.InlineKeyboardButton('Связаться с администратором', callback_data='contact_admin'))

            bot.send_message(chat_id, messages['choose_option_text'], reply_markup=markup, parse_mode='Markdown')
        except Exception as e:
            send_error_message(bot, GROUP_CHAT_ID, f"Ошибка в send_welcome: {str(e)}")
            logger.error(f"Ошибка в send_welcome: {str(e)}", exc_info=True)
