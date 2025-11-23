from utils import send_error_message


def register_analytics_handlers(bot, data):
    GROUP_CHAT_ID = data['GROUP_CHAT_ID']
    unique_visits = data['unique_visits']
    logger = data['logger']
    db = data['db']

    @bot.callback_query_handler(func=lambda call: call.data == 'visit_website')
    def visit_website_handler(call):
        try:
            chat_id = call.message.chat.id
            user_id = call.from_user.id

            if user_id not in unique_visits and not db.has_event_for_user('visit_website', user_id):
                unique_visits.add(user_id)
                db.record_event('visit_website', {'telegram_id': user_id})
                logger.info(f"Уникальный пользователь {user_id} добавлен в аналитику.")

            website_url = 'https://peraperajapanese.tilda.ws/'
            bot.send_message(chat_id, f'Перейдите по ссылке: {website_url}')

            logger.info(f"Пользователь {user_id} получил ссылку на сайт.")
            bot.answer_callback_query(call.id)
        except Exception as e:
            send_error_message(bot, GROUP_CHAT_ID, f"Ошибка в visit_website_handler: {str(e)}")
            logger.error(f"Ошибка в visit_website_handler: {str(e)}", exc_info=True)

    @bot.message_handler(commands=['get_analytics'])
    def get_analytics(message):
        if message.chat.id != GROUP_CHAT_ID:
            bot.send_message(message.chat.id, "Ошибка: эта команда доступна только в группе администраторов.")
            return

        try:
            website_clicks = db.count_unique_events('visit_website')
            bot.send_message(message.chat.id, f"Количество переходов на сайт (уникальных): {website_clicks}")
            logger.info("Команда /get_analytics выполнена успешно")
        except Exception as e:
            send_error_message(bot, GROUP_CHAT_ID, f"Ошибка в get_analytics: {str(e)}")
            logger.error(f"Ошибка в get_analytics: {str(e)}", exc_info=True)

