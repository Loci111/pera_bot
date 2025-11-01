from telebot import types
from utils import send_error_message, save_to_excel

def register_signup_handlers(bot, data):
    users_info = data['users_info']
    pre_signup_info = data['pre_signup_info']
    pre_signup_a1_n5_info = data.get('pre_signup_a1_n5_info', {})
    messages = data['messages']
    GROUP_CHAT_ID = data['GROUP_CHAT_ID']
    excel_file = data['excel_file']
    pre_signup_file = data['pre_signup_file']
    pre_signup_a1_n5_file = data.get('pre_signup_a1_n5_file', 'pre_signup_a1_n5.xlsx')
    logger = data['logger']

    @bot.callback_query_handler(func=lambda call: call.data == 'marathon')
    def marathon_handler(call):
        try:
            chat_id = call.message.chat.id
            bot.send_message(chat_id, messages['marathon_text'], parse_mode='Markdown')

            markup = types.InlineKeyboardMarkup()
            button1 = types.InlineKeyboardButton('ПОДАТЬ ЗАЯВКУ НА МАРАФОН', callback_data='signup')
            markup.add(button1)

            bot.send_message(chat_id, messages['press_button_text'], reply_markup=markup, parse_mode='Markdown')
        except Exception as e:
            send_error_message(bot, GROUP_CHAT_ID, f"Ошибка в marathon_handler: {str(e)}")
            logger.error(f"Ошибка в marathon_handler: {str(e)}", exc_info=True)

    @bot.callback_query_handler(func=lambda call: call.data == 'a1')
    def a1_handler(call):
        try:
            chat_id = call.message.chat.id
            bot.send_message(chat_id, messages['a1_text'])

            markup = types.InlineKeyboardMarkup()
            button1 = types.InlineKeyboardButton('Смотреть программу курса', url='https://peraperajapanese.tilda.ws/a1course')
            button2 = types.InlineKeyboardButton('Анкета предзаписи', callback_data='pre_signup')
            markup.add(button1)
            markup.add(button2)

            bot.send_message(chat_id, messages['pre_signup_text'], reply_markup=markup)
        except Exception as e:
            send_error_message(bot, GROUP_CHAT_ID, f"Ошибка в a1_handler: {str(e)}")
            logger.error(f"Ошибка в a1_handler: {str(e)}", exc_info=True)

    @bot.callback_query_handler(func=lambda call: call.data == 'a1_n5')
    def a1_n5_handler(call):
        try:
            chat_id = call.message.chat.id
            bot.send_message(chat_id, messages['a1_n5_text'])

            markup = types.InlineKeyboardMarkup()
            button1 = types.InlineKeyboardButton('Смотреть программу курса',
                                                 url='https://peraperajapanese.tilda.ws/coursen5')
            button2 = types.InlineKeyboardButton('Анкета предзаписи (A1–N5)', callback_data='pre_signup_a1_n5')
            markup.add(button1)
            markup.add(button2)

            bot.send_message(chat_id, "Нажимай, чтобы записаться или изучить программу:", reply_markup=markup)
        except Exception as e:
            send_error_message(bot, GROUP_CHAT_ID, f"Ошибка в a1_n5_handler: {str(e)}")
            logger.error(f"Ошибка в a1_n5_handler: {str(e)}", exc_info=True)

    @bot.callback_query_handler(func=lambda call: call.data == 'signup')
    def signup_handler(call):
        try:
            user_id = call.from_user.id
            username = call.from_user.username if call.from_user.username else "Нет никнейма"
            user_info = users_info.get(user_id, {})

            logger.info(f"Пользователь @{username} (ID: {user_id}) хочет записаться на марафон.")

            user_info.update({
                'chat_id': user_id,
                'username': username,
                'signup': True
            })

            users_info[user_id] = user_info

            if save_to_excel(user_info, filename=excel_file, logger=logger):
                logger.info(f"Данные пользователя @{username} (ID: {user_id}) успешно сохранены в {excel_file}.")
                bot.send_message(call.message.chat.id, messages['signup_success_text'], parse_mode='Markdown')
                bot.send_message(GROUP_CHAT_ID, f"Новый пользователь записался на марафон @{username} (ID: {user_id})", disable_notification=True)
            else:
                bot.send_message(call.message.chat.id, messages['already_signed_up_text'], parse_mode='Markdown')
            bot.answer_callback_query(call.id)
        except Exception as e:
            send_error_message(bot, GROUP_CHAT_ID, f"Ошибка в signup_handler: {str(e)}")
            logger.error(f"Ошибка в signup_handler: {str(e)}", exc_info=True)

    @bot.callback_query_handler(func=lambda call: call.data == 'pre_signup')
    def pre_signup_handler(call):
        try:
            user_id = call.from_user.id
            username = call.from_user.username if call.from_user.username else "Нет никнейма"
            chat_id = call.message.chat.id

            logger.info(f"Пользователь @{username} (ID: {user_id}) хочет подать анкету на предзапись курса A1.")

            user_info = pre_signup_info.get(user_id, {})
            user_info.update({
                'chat_id': user_id,
                'username': username,
                'comment': 'pre-signup A1'
            })
            pre_signup_info[user_id] = user_info

            if save_to_excel(user_info, filename=pre_signup_file, logger=logger):
                bot.send_message(chat_id, messages['pre_signup_success_text'], parse_mode='Markdown')
                bot.send_message(GROUP_CHAT_ID, f"Новая предзапись на курс A1: @{username} (ID: {user_id})",
                                 disable_notification=True)
            else:
                bot.send_message(chat_id, messages['already_signed_up_text'], parse_mode='Markdown')

            bot.answer_callback_query(call.id)
        except Exception as e:
            send_error_message(bot, GROUP_CHAT_ID, f"Ошибка в pre_signup_handler: {str(e)}")
            logger.error(f"Ошибка в pre_signup_handler: {str(e)}", exc_info=True)

    @bot.callback_query_handler(func=lambda call: call.data == 'pre_signup_a1_n5')
    def pre_signup_a1_n5_handler(call):
        try:
            user_id = call.from_user.id
            username = call.from_user.username if call.from_user.username else "Нет никнейма"
            chat_id = call.message.chat.id

            user_info = pre_signup_a1_n5_info.get(user_id, {})
            user_info.update({
                'chat_id': user_id,
                'username': username,
                'comment': 'pre-signup A1–N5'
            })
            pre_signup_a1_n5_info[user_id] = user_info

            if save_to_excel(user_info, filename=pre_signup_a1_n5_file, logger=logger):
                bot.send_message(chat_id, messages['a1_n5_pre_signup_success_text'], parse_mode='Markdown')
                bot.send_message(GROUP_CHAT_ID, f"Новая предзапись на курс A1–N5: @{username} (ID: {user_id})", disable_notification=True)
            else:
                bot.send_message(chat_id, messages['a1_n5_already_signed_up_text'], parse_mode='Markdown')

            bot.answer_callback_query(call.id)
        except Exception as e:
            send_error_message(bot, GROUP_CHAT_ID, f"Ошибка в pre_signup_a1_n5_handler: {str(e)}")
            logger.error(f"Ошибка в pre_signup_a1_n5_handler: {str(e)}", exc_info=True)
