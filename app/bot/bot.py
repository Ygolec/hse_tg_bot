import os
import logging
import telebot
from telebot import types
from app.services.directus import get_bus_schedule
from app.services.webapp import check_checkin_status, check_relocation_status


logger = logging.getLogger(__name__)

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
    
    @bot.message_handler(commands=['start'])
    def start_command(message):
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
            bot.send_message(message.chat.id, status)
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
            bot.send_message(message.chat.id, status)
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
    
    markup.add(checkin_btn, relocation_btn)
    markup.add(bus_schedule_btn)
    
    return markup