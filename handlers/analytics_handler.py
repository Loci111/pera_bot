from utils import send_error_message, save_json_data, load_json_data

def register_analytics_handlers(bot, data):
    analytics_data = data['analytics_data']
    GROUP_CHAT_ID = data['GROUP_CHAT_ID']
    analytics_file = data['analytics_file']
    unique_visits = data['unique_visits']
    logger = data['logger']

    @bot.callback_query_handler(func=lambda call: call.data == 'visit_website')
    def visit_website_handler(call):
        try:
            chat_id = call.message.chat.id
            user_id = call.from_user.id

            # Учитываем только уникальных пользователей
            if user_id not in unique_visits:
                unique_visits.add(user_id)
                analytics_data['website_clicks'] += 1
                save_json_data(analytics_file, analytics_data)
                logger.info(f"Уникальный пользователь {user_id} добавлен в аналитику.")

            # Отправляем ссылку пользователю
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
            # Загружаем данные из файла аналитики
            analytics_data = load_json_data(analytics_file, {"website_clicks": 0})
            website_clicks = analytics_data.get('website_clicks', 0)

            # Отправляем количество уникальных переходов
            bot.send_message(message.chat.id, f"Количество переходов на сайт (уникальных): {website_clicks}")
            logger.info("Команда /get_analytics выполнена успешно")
        except Exception as e:
            send_error_message(bot, GROUP_CHAT_ID, f"Ошибка в get_analytics: {str(e)}")
            logger.error(f"Ошибка в get_analytics: {str(e)}", exc_info=True)
