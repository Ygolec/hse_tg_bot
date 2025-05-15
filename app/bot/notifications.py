import logging
import os
from telebot import TeleBot


logger = logging.getLogger(__name__)

_bot_instance = None

def get_bot_instance():
    global _bot_instance
    if _bot_instance is None:
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not token:
            logger.error("Telegram bot token not found in environment variables")
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable is not set")
        
        _bot_instance = TeleBot(token)
        logger.info("Created new bot instance for notifications")
    
    return _bot_instance

def send_notification(user_id, notification_type, message, status=None):
    try:
        bot = get_bot_instance()

        formatted_message = format_notification(notification_type, message, status)

        bot.send_message(user_id, formatted_message)
        
        logger.info(f"Notification sent to user {user_id} (type: {notification_type})")
        return True
    
    except Exception as e:
        logger.error(f"Failed to send notification to user {user_id}: {e}")
        return False

def format_notification(notification_type, message, status=None):
    if notification_type == "checkin":
        header = "📢 Уведомление о заселении"
    elif notification_type == "relocation":
        header = "📢 Уведомление о переселении"
    else:  # general
        header = "📢 Общее уведомление"
    
    formatted_message = f"{header}\n\n{message}"
    
    if status:
        formatted_message += f"\n\nСтатус: {status}"
    
    return formatted_message