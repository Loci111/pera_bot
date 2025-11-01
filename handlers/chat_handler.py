# handlers/chat_handler.py

def register_chat_handlers(bot, data):
    GROUP_CHAT_ID = data['GROUP_CHAT_ID']
    message_user_map = data['message_user_map']
    logger = data['logger']

    @bot.callback_query_handler(func=lambda call: call.data == 'contact_admin')
    def contact_admin_handler(call):
        try:
            chat_id = call.message.chat.id
            bot.send_message(chat_id, "Ты можешь отправить мне сообщение, и я передам его администратору.")
            bot.answer_callback_query(call.id)
        except Exception as e:
            logger.error(f"Ошибка в contact_admin_handler: {str(e)}", exc_info=True)

    @bot.message_handler(func=lambda message: message.chat.type == 'private', content_types=['text', 'photo', 'voice', 'document', 'video', 'audio', 'sticker'])
    def user_message_handler(message):
        try:
            user_id = message.from_user.id
            chat_id = message.chat.id

            user_info = f"Сообщение от @{message.from_user.username or message.from_user.first_name} (ID: {user_id}):"

            if message.content_type == 'text':
                forwarded_message = bot.send_message(GROUP_CHAT_ID, f"{user_info}\n{message.text}")
            else:
                # Обработка других типов сообщений
                caption = message.caption if message.caption else ""
                caption = f"{user_info}\n{caption}"

                if message.content_type == 'photo':
                    file_id = message.photo[-1].file_id
                    forwarded_message = bot.send_photo(GROUP_CHAT_ID, file_id, caption=caption)
                elif message.content_type == 'document':
                    file_id = message.document.file_id
                    forwarded_message = bot.send_document(GROUP_CHAT_ID, file_id, caption=caption)
                elif message.content_type == 'voice':
                    file_id = message.voice.file_id
                    forwarded_message = bot.send_voice(GROUP_CHAT_ID, file_id, caption=caption)
                elif message.content_type == 'video':
                    file_id = message.video.file_id
                    forwarded_message = bot.send_video(GROUP_CHAT_ID, file_id, caption=caption)
                elif message.content_type == 'audio':
                    file_id = message.audio.file_id
                    forwarded_message = bot.send_audio(GROUP_CHAT_ID, file_id, caption=caption)
                elif message.content_type == 'sticker':
                    file_id = message.sticker.file_id
                    forwarded_message = bot.send_sticker(GROUP_CHAT_ID, file_id)
                    bot.send_message(GROUP_CHAT_ID, user_info)
                else:
                    # Для других типов контента просто пересылаем сообщение
                    forwarded_message = bot.forward_message(GROUP_CHAT_ID, chat_id, message.message_id)
                    bot.send_message(GROUP_CHAT_ID, user_info)

            # Сохраняем соответствие между сообщением администратора и ID пользователя
            message_user_map[forwarded_message.message_id] = user_id
        except Exception as e:
            logger.error(f"Ошибка в user_message_handler: {str(e)}", exc_info=True)

    @bot.message_handler(func=lambda message: message.chat.id == GROUP_CHAT_ID and message.reply_to_message is not None)
    def admin_reply_handler(message):
        try:
            if message.reply_to_message.message_id in message_user_map:
                user_id = message_user_map[message.reply_to_message.message_id]
                # Отправляем ответ пользователю
                if message.content_type == 'text':
                    bot.send_message(user_id, message.text)
                else:
                    # Обработка других типов сообщений
                    caption = message.caption if message.caption else ""

                    if message.content_type == 'photo':
                        file_id = message.photo[-1].file_id
                        bot.send_photo(user_id, file_id, caption=caption)
                    elif message.content_type == 'document':
                        file_id = message.document.file_id
                        bot.send_document(user_id, file_id, caption=caption)
                    elif message.content_type == 'voice':
                        file_id = message.voice.file_id
                        bot.send_voice(user_id, file_id, caption=caption)
                    elif message.content_type == 'video':
                        file_id = message.video.file_id
                        bot.send_video(user_id, file_id, caption=caption)
                    elif message.content_type == 'audio':
                        file_id = message.audio.file_id
                        bot.send_audio(user_id, file_id, caption=caption)
                    elif message.content_type == 'sticker':
                        file_id = message.sticker.file_id
                        bot.send_sticker(user_id, file_id)
                    else:
                        # Для других типов контента просто пересылаем сообщение
                        bot.forward_message(user_id, GROUP_CHAT_ID, message.message_id)
            else:
                bot.send_message(GROUP_CHAT_ID, "Ошибка: Не могу определить пользователя для ответа.")
        except Exception as e:
            logger.error(f"Ошибка в admin_reply_handler: {str(e)}", exc_info=True)
