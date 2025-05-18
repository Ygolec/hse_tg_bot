import os
import logging
import telebot
from telebot import types
from app.services.directus import get_bus_schedule
from app.services.webapp import check_checkin_status, check_relocation_status
from app.services.llm_rag import ask_llm_rag


logger = logging.getLogger(__name__)


user_conversation_state = {}

def setup_bot():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("Telegram bot token not found in environment variables")
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable is not set")

    bot = telebot.TeleBot(token)
    logger.info("Telegram bot initialized")

    register_handlers(bot)

    return bot

def register_handlers(bot):
    global user_conversation_state


    logger.info(f"Initial user_conversation_state: {user_conversation_state}")

    @bot.message_handler(commands=['start'])
    def start_command(message):

        if message.from_user.id in user_conversation_state:
            del user_conversation_state[message.from_user.id]

        markup = create_main_keyboard()
        bot.send_message(
            message.chat.id,
            "Привет! Я бот для помощи с общежитием. Выберите опцию:",
            reply_markup=markup
        )
        logger.info(f"Start command received from user {message.from_user.id}")

    @bot.message_handler(commands=['help'])
    def help_command(message):
        help_text = (
            "Доступные команды:\n"
            "/start - Начать взаимодействие с ботом\n"
            "/help - Показать эту справку\n\n"
            "Кнопки:\n"
            "Заселение - Проверить статус заселения\n"
            "Переселение - Проверить статус переселения\n"
            "Расписание автобусов - Получить актуальное расписание автобусов"
        )
        bot.send_message(message.chat.id, help_text)
        logger.info(f"Help command received from user {message.from_user.id}")

    @bot.message_handler(func=lambda message: message.text == "Заселение")
    def checkin_handler(message):
        logger.info(f"Check-in request from user {message.from_user.id}")
        try:
            status = check_checkin_status(message.from_user.id)
            bot.send_message(message.chat.id, status,parse_mode="HTML")
        except Exception as e:
            logger.error(f"Error processing check-in request: {e}")
            bot.send_message(
                message.chat.id,
                "Произошла ошибка при получении информации о заселении. Пожалуйста, попробуйте позже."
            )

    @bot.message_handler(func=lambda message: message.text == "Переселение")
    def relocation_handler(message):
        logger.info(f"Relocation request from user {message.from_user.id}")
        try:
            status = check_relocation_status(message.from_user.id)
            bot.send_message(message.chat.id, status, parse_mode="HTML")
        except Exception as e:
            logger.error(f"Error processing relocation request: {e}")
            bot.send_message(
                message.chat.id,
                "Произошла ошибка при получении информации о переселении. Пожалуйста, попробуйте позже."
            )

    @bot.message_handler(func=lambda message: message.text == "Расписание автобусов")
    def bus_schedule_handler(message):
        logger.info(f"Bus schedule request from user {message.from_user.id}")
        try:
            schedule = get_bus_schedule()
            print(schedule['image_url'])
            if schedule and 'image_url' in schedule:
                bot.send_photo(
                    message.chat.id,
                    schedule['image_url'] + "?download",
                    caption="Актуальное расписание автобусов"
                )
            else:
                bot.send_message(
                    message.chat.id,
                    "Расписание автобусов временно недоступно."
                )
        except Exception as e:
            logger.error(f"Error processing bus schedule request: {e}")
            bot.send_message(
                message.chat.id,
                "Произошла ошибка при получении расписания автобусов. Пожалуйста, попробуйте позже."
            )

    @bot.message_handler(func=lambda message: message.text == "Нейровопрос")
    def neural_question_handler(message):
        try:
            user_id = message.from_user.id
            chat_id = message.chat.id

            logger.info(f"Neural question request from user {user_id}")

            logger.info(f"Before creating markup for user {user_id}")

            markup = types.InlineKeyboardMarkup()
            start_btn = types.InlineKeyboardButton("Начать", callback_data="start_conversation")
            markup.add(start_btn)
            logger.info(f"After creating markup for user {user_id}, button data: {start_btn.callback_data}")


            markup_json = {
                'inline_keyboard': [
                    [{'text': 'Начать', 'callback_data': 'start_conversation'}]
                ]
            }
            logger.info(f"Created JSON markup for user {user_id}: {markup_json}")

            logger.info(f"Before sending messages to user {user_id}")


            sent_message1 = bot.send_message(
                chat_id,
                "Здесь вы можете задать вопросы по заселению в общежитие. "
                "Нейросеть постарается ответить на ваши вопросы максимально точно. "
                "Нажмите 'Начать', чтобы начать разговор.",
                reply_markup=markup
            )
            logger.info(f"Sent message with standard markup to user {user_id}, message_id: {sent_message1.message_id}")



            logger.info(f"After sending messages to user {user_id}")
        except Exception as e:
            import traceback
            error_traceback = traceback.format_exc()
            logger.error(f"Error in neural_question_handler: {e}")
            logger.error(f"Traceback: {error_traceback}")


            try:
                bot.send_message(
                    message.chat.id,
                    "Произошла ошибка при подготовке нейровопроса. Пожалуйста, попробуйте позже."
                )
            except Exception as notify_error:
                logger.error(f"Failed to notify user about error: {notify_error}")

    @bot.callback_query_handler(func=lambda call: call.data == "start_conversation")
    def start_conversation_callback(call):
        try:
            logger.info(f"Callback received: {call.data} from user {call.from_user.id}")
            user_id = call.from_user.id
            chat_id = call.message.chat.id
            message_text = call.message.text if hasattr(call.message, 'text') else ""

            logger.info(f"Message text: {message_text}")

            logger.info(f"Before acknowledging callback query for user {user_id}")

            bot.answer_callback_query(call.id)
            logger.info(f"After acknowledging callback query for user {user_id}")

            logger.info(f"Starting conversation with user {user_id}")

            logger.info(f"Before updating user_conversation_state for user {user_id}")

            user_conversation_state[user_id] = True
            logger.info(f"After updating user_conversation_state for user {user_id}, current state: {user_conversation_state}")

            logger.info(f"Before creating markup for user {user_id}")

            markup = types.InlineKeyboardMarkup()
            end_btn = types.InlineKeyboardButton("Завершить разговор", callback_data="end_conversation")
            markup.add(end_btn)
            logger.info(f"After creating markup for user {user_id}")


            markup_json = {
                'inline_keyboard': [
                    [{'text': 'Завершить разговор', 'callback_data': 'end_conversation'}]
                ]
            }

            logger.info(f"Before updating message for user {user_id}")


            is_alternative = "Альтернативный вариант" in message_text


            try:
                if is_alternative:
                    logger.info(f"Editing alternative message for user {user_id}")

                    import json
                    bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=call.message.message_id,
                        text="Разговор начат (альтернативный вариант). Задайте ваш вопрос по заселению в общежитие.",
                        reply_markup=json.dumps(markup_json)
                    )
                else:

                    bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=call.message.message_id,
                        text="Разговор начат. Задайте ваш вопрос по заселению в общежитие.",
                        reply_markup=markup
                    )
                logger.info(f"Successfully edited message for user {user_id}")
            except Exception as edit_error:
                logger.error(f"Error editing message: {edit_error}")

                try:
                    sent_message = bot.send_message(
                        chat_id,
                        "Разговор начат. Задайте ваш вопрос по заселению в общежитие.",
                        reply_markup=markup
                    )
                    logger.info(f"Sent new message for user {user_id}, message_id: {sent_message.message_id}")
                except Exception as send_error:
                    logger.error(f"Error sending new message: {send_error}")

                    try:
                        import json
                        sent_message = bot.send_message(
                            chat_id,
                            "Разговор начат (альтернативный вариант). Задайте ваш вопрос по заселению в общежитие.",
                            reply_markup=json.dumps(markup_json)
                        )
                        logger.info(f"Sent new message with JSON markup for user {user_id}, message_id: {sent_message.message_id}")
                    except Exception as json_error:
                        logger.error(f"Error sending message with JSON markup: {json_error}")

            logger.info(f"After updating message for user {user_id}")
        except Exception as e:
            import traceback
            error_traceback = traceback.format_exc()
            logger.error(f"Error in start_conversation_callback: {e}")
            logger.error(f"Traceback: {error_traceback}")


            try:
                bot.send_message(
                    call.message.chat.id,
                    "Произошла ошибка при начале разговора. Пожалуйста, попробуйте позже."
                )
            except Exception as notify_error:
                logger.error(f"Failed to notify user about error: {notify_error}")

    @bot.callback_query_handler(func=lambda call: call.data == "end_conversation")
    def end_conversation_callback(call):
        try:
            logger.info(f"End conversation callback received: {call.data} from user {call.from_user.id}")
            user_id = call.from_user.id
            chat_id = call.message.chat.id
            message_text = call.message.text if hasattr(call.message, 'text') else ""

            logger.info(f"Message text: {message_text}")

            logger.info(f"Before acknowledging callback query for user {user_id}")

            bot.answer_callback_query(call.id)
            logger.info(f"After acknowledging callback query for user {user_id}")

            logger.info(f"Ending conversation with user {user_id}")

            logger.info(f"Before removing user from conversation_state, current state: {user_conversation_state}")

            if user_id in user_conversation_state:
                del user_conversation_state[user_id]
                logger.info(f"User {user_id} removed from conversation_state")
            else:
                logger.warning(f"User {user_id} not found in conversation_state")
            logger.info(f"After removing user from conversation_state, current state: {user_conversation_state}")

            logger.info(f"Before creating main keyboard for user {user_id}")
            markup = create_main_keyboard()
            logger.info(f"After creating main keyboard for user {user_id}")


            is_alternative = "альтернативный вариант" in message_text.lower()

            logger.info(f"Before sending end message to user {user_id}")
            try:

                if is_alternative:
                    logger.info(f"Trying to edit alternative message for user {user_id}")
                    try:

                        raise Exception("Can't edit alternative message with ReplyKeyboardMarkup")
                    except Exception as edit_error:
                        logger.error(f"Error editing alternative message: {edit_error}")
                else:
                    logger.info(f"Trying to edit standard message for user {user_id}")
                    try:

                        bot.edit_message_text(
                            chat_id=chat_id,
                            message_id=call.message.message_id,
                            text="Разговор завершен. Отправляю главное меню..."
                        )
                        logger.info(f"Successfully edited message for user {user_id}")
                    except Exception as edit_error:
                        logger.error(f"Error editing message: {edit_error}")


                sent_message = bot.send_message(
                    chat_id,
                    "Разговор завершен. Вы можете выбрать другую опцию:",
                    reply_markup=markup
                )
                logger.info(f"Sent end message to user {user_id}, message_id: {sent_message.message_id}")
            except Exception as send_error:
                logger.error(f"Error sending end message: {send_error}")

                try:
                    bot.send_message(
                        chat_id,
                        "Разговор завершен.",
                        reply_markup=types.ReplyKeyboardRemove()
                    )
                    logger.info(f"Sent simple end message to user {user_id}")


                    bot.send_message(
                        chat_id,
                        "Выберите опцию:",
                        reply_markup=markup
                    )
                    logger.info(f"Sent main keyboard to user {user_id}")
                except Exception as simple_error:
                    logger.error(f"Error sending simple end message: {simple_error}")

            logger.info(f"After sending end message to user {user_id}")
        except Exception as e:
            import traceback
            error_traceback = traceback.format_exc()
            logger.error(f"Error in end_conversation_callback: {e}")
            logger.error(f"Traceback: {error_traceback}")


            try:
                bot.send_message(
                    call.message.chat.id,
                    "Произошла ошибка при завершении разговора. Пожалуйста, попробуйте позже."
                )
            except Exception as notify_error:
                logger.error(f"Failed to notify user about error: {notify_error}")

    @bot.message_handler(func=lambda message: message.from_user.id in user_conversation_state)
    def conversation_handler(message):
        try:
            user_id = message.from_user.id
            chat_id = message.chat.id

            logger.info(f"Processing question from user {user_id}: {message.text}")
            logger.info(f"User conversation state: {user_conversation_state}")

            logger.info(f"Before creating markup for user {user_id}")

            markup = types.InlineKeyboardMarkup()
            end_btn = types.InlineKeyboardButton("Завершить разговор", callback_data="end_conversation")
            markup.add(end_btn)
            logger.info(f"After creating markup for user {user_id}")

            logger.info(f"Before sending typing action to user {user_id}")

            bot.send_chat_action(chat_id, 'typing')
            logger.info(f"After sending typing action to user {user_id}")

            logger.info(f"Before calling ask_llm_rag for user {user_id}")

            response = ask_llm_rag(message.text)
            logger.info(f"After calling ask_llm_rag for user {user_id}")

            logger.info(f"Received response from LLM RAG API: {response}")


            answer = "Извините, я не смог найти ответ на ваш вопрос. Пожалуйста, попробуйте переформулировать вопрос."

            logger.info(f"Before processing response for user {user_id}")
            if response:

                if 'error' in response and 'detail' in response:
                    logger.error(f"API returned an error: {response['error']}")
                    answer = response['detail']

                elif 'detail' in response:
                    answer = response['detail']
                elif 'answer' in response:
                    answer = response['answer']
                elif 'response' in response:
                    answer = response['response']
                elif 'text' in response:
                    answer = response['text']
                elif isinstance(response, str):
                    answer = response
            logger.info(f"After processing response for user {user_id}")

            logger.info(f"Final answer to user: {answer[:100]}...")

            logger.info(f"Before sending answer to user {user_id}")
            sent_message = bot.send_message(
                chat_id,
                answer,
                reply_markup=markup
            )
            logger.info(f"After sending answer to user {user_id}, message_id: {sent_message.message_id}")
        except Exception as e:
            import traceback
            error_traceback = traceback.format_exc()
            logger.error(f"Error processing question: {e}")
            logger.error(f"Traceback: {error_traceback}")

            try:

                markup = types.InlineKeyboardMarkup()
                end_btn = types.InlineKeyboardButton("Завершить разговор", callback_data="end_conversation")
                markup.add(end_btn)

                bot.send_message(
                    chat_id,
                    "Произошла ошибка при обработке вашего вопроса. Пожалуйста, попробуйте позже.",
                    reply_markup=markup
                )
            except Exception as notify_error:
                logger.error(f"Failed to notify user about error: {notify_error}")

    @bot.message_handler(func=lambda message: True)
    def default_handler(message):
        markup = create_main_keyboard()
        bot.send_message(
            message.chat.id,
            "Пожалуйста, используйте кнопки для взаимодействия с ботом.",
            reply_markup=markup
        )
        logger.info(f"Default handler triggered for user {message.from_user.id}")

    logger.info("All handlers registered")

def create_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    checkin_btn = types.KeyboardButton("Заселение")
    relocation_btn = types.KeyboardButton("Переселение")
    bus_schedule_btn = types.KeyboardButton("Расписание автобусов")
    neural_question_btn = types.KeyboardButton("Нейровопрос")

    markup.add(checkin_btn, relocation_btn)
    markup.add(bus_schedule_btn, neural_question_btn)

    return markup
