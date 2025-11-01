from telebot import types
from utils import send_error_message

def register_materials_handlers(bot, data):
    materials = data['materials']
    GROUP_CHAT_ID = data['GROUP_CHAT_ID']

    @bot.callback_query_handler(func=lambda call: call.data == 'download_materials')
    def download_materials_handler(call):
        try:
            chat_id = call.message.chat.id

            # Создаем клавиатуру с материалами
            markup = types.InlineKeyboardMarkup()
            for material in materials:
                button = types.InlineKeyboardButton(material['name'], callback_data=f'download_{material["id"]}')
                markup.add(button)

            bot.send_message(chat_id, 'Выбери материал для скачивания:', reply_markup=markup)
        except Exception as e:
            send_error_message(bot, GROUP_CHAT_ID, f"Ошибка в download_materials_handler: {str(e)}")
            logger.error(f"Ошибка в download_materials_handler: {str(e)}", exc_info=True)

    @bot.callback_query_handler(func=lambda call: call.data.startswith('download_'))
    def send_material_handler(call):
        try:
            chat_id = call.message.chat.id
            material_id = call.data.split('download_', 1)[1]

            # Найти материал по ID
            material = next((m for m in materials if m['id'] == material_id), None)

            if material:
                # Отправить ссылку для скачивания
                download_link = "https://drive.google.com/file/d/1tqys7Ge15zuDLWmcnXvcDvZh9wnEOldg/view?usp=sharing"
                bot.send_message(chat_id, f"Можешь скачать гайд по ссылке: {download_link}")
            else:
                bot.send_message(chat_id, 'К сожалению, выбранный материал не найден.')
        except Exception as e:
            send_error_message(bot, GROUP_CHAT_ID, f"Ошибка в send_material_handler: {str(e)}")
            logger.error(f"Ошибка в send_material_handler: {str(e)}", exc_info=True)
