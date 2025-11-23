from utils import send_error_message

from .signup_handler import PRE_SIGNUP_A1_N5_EVENT, PRE_SIGNUP_EVENT, SIGNUP_EVENT


def register_broadcast_handlers(bot, data):
    GROUP_CHAT_ID = data['GROUP_CHAT_ID']
    db = data['db']
    logger = data['logger']

    @bot.message_handler(commands=['broadcast'])
    def broadcast_message(message):
        if message.chat.id != GROUP_CHAT_ID:
            bot.send_message(message.chat.id, "Ошибка: эта команда доступна только в группе администраторов.")
            return

        try:
            if len(message.text.split()) < 2:
                bot.send_message(message.chat.id,
                                 "Ошибка: пустое сообщение. Пожалуйста, используйте команду /broadcast <текст сообщения>.")
                return
            text = message.text.split(' ', 1)[1]
            user_ids = db.get_users_by_event(SIGNUP_EVENT)
            for user_id in user_ids:
                try:
                    bot.send_message(user_id, text)
                    logger.info(f"Broadcast message sent to {user_id}")
                except Exception as e:
                    logger.error(f"Failed to send message to {user_id}: {str(e)}", exc_info=True)
            bot.send_message(message.chat.id, "Рассылка завершена.")
        except Exception as e:
            send_error_message(bot, GROUP_CHAT_ID, f"Ошибка в broadcast_message: {str(e)}")
            logger.error(f"Ошибка в broadcast_message: {str(e)}", exc_info=True)

    @bot.message_handler(commands=['prebroadcast'])
    def pre_broadcast_message(message):
        if message.chat.id != GROUP_CHAT_ID:
            bot.send_message(message.chat.id, "Ошибка: эта команда доступна только в группе администраторов.")
            return

        try:
            if len(message.text.split()) < 2:
                bot.send_message(message.chat.id,
                                 "Ошибка: пустое сообщение. Пожалуйста, используйте команду /prebroadcast <текст сообщения>.")
                return
            text = message.text.split(' ', 1)[1]
            user_ids = db.get_users_by_event(PRE_SIGNUP_EVENT)
            for user_id in user_ids:
                try:
                    bot.send_message(user_id, text)
                    logger.info(f"Pre-broadcast message sent to {user_id}")
                except Exception as e:
                    logger.error(f"Failed to send message to {user_id}: {str(e)}", exc_info=True)
            bot.send_message(message.chat.id, "Рассылка завершена.")
        except Exception as e:
            send_error_message(bot, GROUP_CHAT_ID, f"Ошибка в pre_broadcast_message: {str(e)}")
            logger.error(f"Ошибка в pre_broadcast_message: {str(e)}", exc_info=True)

    @bot.message_handler(commands=['list_users'])
    def list_users(message):
        if message.chat.id != GROUP_CHAT_ID:
            bot.send_message(message.chat.id, "Ошибка: эта команда доступна только в группе администраторов.")
            return

        try:
            users = db.get_all_users()
            users_list = "Список пользователей (users):\n"
            for user in users:
                users_list += f"Username: {user.get('username')}, UserID: {user.get('telegram_id')}\n"
            bot.send_message(message.chat.id, users_list)
            logger.info("Команда /list_users выполнена успешно")
        except Exception as e:
            send_error_message(bot, GROUP_CHAT_ID, f"Ошибка в list_users: {str(e)}")
            logger.error(f"Ошибка в list_users: {str(e)}", exc_info=True)

    @bot.message_handler(commands=['list_pre_signup'])
    def list_pre_signup(message):
        if message.chat.id != GROUP_CHAT_ID:
            bot.send_message(message.chat.id, "Ошибка: эта команда доступна только в группе администраторов.")
            return

        try:
            user_ids = db.get_users_by_event(PRE_SIGNUP_EVENT)
            pre_signup_list = "Список пользователей (pre_signup_info):\n"
            for user_id in user_ids:
                pre_signup_list += f"UserID: {user_id}\n"
            bot.send_message(message.chat.id, pre_signup_list)
            logger.info("Команда /list_pre_signup выполнена успешно")
        except Exception as e:
            send_error_message(bot, GROUP_CHAT_ID, f"Ошибка в list_pre_signup: {str(e)}")
            logger.error(f"Ошибка в list_pre_signup: {str(e)}", exc_info=True)

    @bot.message_handler(commands=['list_pre_signup_a1_n5'])
    def list_pre_signup_a1_n5(message):
        if message.chat.id != GROUP_CHAT_ID:
            bot.send_message(message.chat.id, "Ошибка: эта команда доступна только в группе администраторов.")
            return

        try:
            user_ids = db.get_users_by_event(PRE_SIGNUP_A1_N5_EVENT)
            pre_signup_list = "Список пользователей (A1–N5):\n"
            for user_id in user_ids:
                pre_signup_list += f"UserID: {user_id}\n"
            bot.send_message(message.chat.id, pre_signup_list)
            logger.info("Команда /list_pre_signup_a1_n5 выполнена успешно")
        except Exception as e:
            send_error_message(bot, GROUP_CHAT_ID, f"Ошибка в list_pre_signup_a1_n5: {str(e)}")
            logger.error(f"Ошибка в list_pre_signup_a1_n5: {str(e)}", exc_info=True)

    @bot.message_handler(commands=['reply'])
    def reply_to_user(message):
        if message.chat.id != GROUP_CHAT_ID:
            bot.send_message(message.chat.id, "Ошибка: эта команда доступна только в группе администраторов.")
            return

        try:
            command_parts = message.text.split(' ', 2)
            if len(command_parts) < 3:
                bot.send_message(message.chat.id, "Ошибка: неверный формат команды. Используйте: /reply <user_id> <сообщение>")
                return

            user_id = int(command_parts[1])
            text = command_parts[2]

            response = bot.send_message(user_id, text)
            bot.send_message(message.chat.id, "Сообщение успешно отправлено.")
            logger.info(f"Сообщение успешно отправлено пользователю {user_id}. Message ID: {response.message_id}")
        except Exception as e:
            send_error_message(bot, GROUP_CHAT_ID, f"Ошибка в reply_to_user: {str(e)}")
            logger.error(f"Ошибка в reply_to_user: {str(e)}", exc_info=True)

