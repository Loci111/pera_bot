from telebot import types
from utils import send_error_message


SIGNUP_EVENT = 'signup'
PRE_SIGNUP_EVENT = 'pre_signup'
PRE_SIGNUP_A1_N5_EVENT = 'pre_signup_a1_n5'

# True = идёт набор на курс (до 17.05.2026), кнопка предзаписи скрыта
# False = режим предзаписи (после 17.05.2026), вернуть кнопку "Анкета предзаписи"
A1_N5_ENROLLMENT_OPEN = True


def register_signup_handlers(bot, data):
    messages = data['messages']
    GROUP_CHAT_ID = data['GROUP_CHAT_ID']
    logger = data['logger']
    db = data['db']

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

            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('Смотреть программу курса',
                                                  url='https://peraperajapanese.tilda.ws/coursen5'))

            if A1_N5_ENROLLMENT_OPEN:
                bot.send_message(chat_id, messages['a1_n5_enrollment_text'])
            else:
                markup.add(types.InlineKeyboardButton('Анкета предзаписи (A1–N5)', callback_data='pre_signup_a1_n5'))
                bot.send_message(chat_id, messages['a1_n5_text'])

            bot.send_message(chat_id, "Нажимай, чтобы записаться или изучить программу:", reply_markup=markup)
        except Exception as e:
            send_error_message(bot, GROUP_CHAT_ID, f"Ошибка в a1_n5_handler: {str(e)}")
            logger.error(f"Ошибка в a1_n5_handler: {str(e)}", exc_info=True)

    @bot.callback_query_handler(func=lambda call: call.data == 'signup')
    def signup_handler(call):
        try:
            user_id = call.from_user.id
            username = call.from_user.username if call.from_user.username else "Нет никнейма"

            db.upsert_user(
                telegram_id=user_id,
                username=username,
                first_name=call.from_user.first_name,
                last_name=call.from_user.last_name,
            )

            logger.info(f"Пользователь @{username} (ID: {user_id}) хочет записаться на марафон.")

            if not db.has_event_for_user(SIGNUP_EVENT, user_id):
                db.record_event(SIGNUP_EVENT, {'telegram_id': user_id, 'username': username})
                logger.info(f"Данные пользователя @{username} (ID: {user_id}) успешно сохранены в базе данных.")
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

            db.upsert_user(
                telegram_id=user_id,
                username=username,
                first_name=call.from_user.first_name,
                last_name=call.from_user.last_name,
            )

            logger.info(f"Пользователь @{username} (ID: {user_id}) хочет подать анкету на предзапись курса A1.")

            if not db.has_event_for_user(PRE_SIGNUP_EVENT, user_id):
                db.record_event(PRE_SIGNUP_EVENT, {'telegram_id': user_id, 'username': username, 'comment': 'pre-signup A1'})
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

            db.upsert_user(
                telegram_id=user_id,
                username=username,
                first_name=call.from_user.first_name,
                last_name=call.from_user.last_name,
            )

            if not db.has_event_for_user(PRE_SIGNUP_A1_N5_EVENT, user_id):
                db.record_event(
                    PRE_SIGNUP_A1_N5_EVENT,
                    {'telegram_id': user_id, 'username': username, 'comment': 'pre-signup A1–N5'},
                )
                bot.send_message(chat_id, messages['a1_n5_pre_signup_success_text'], parse_mode='Markdown')
                bot.send_message(GROUP_CHAT_ID, f"Новая предзапись на курс A1–N5: @{username} (ID: {user_id})", disable_notification=True)
            else:
                bot.send_message(chat_id, messages['a1_n5_already_signed_up_text'], parse_mode='Markdown')

            bot.answer_callback_query(call.id)
        except Exception as e:
            send_error_message(bot, GROUP_CHAT_ID, f"Ошибка в pre_signup_a1_n5_handler: {str(e)}")
            logger.error(f"Ошибка в pre_signup_a1_n5_handler: {str(e)}", exc_info=True)

