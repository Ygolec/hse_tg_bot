import logging
import os
from telebot import TeleBot


logger = logging.getLogger(__name__)


def send_notification(bot, user_id, notification_type, message, status=None):
    try:

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
    else:
        header = "📢 Общее уведомление"
    
    formatted_message = f"{header}\n\n{message}"
    
    # if status:
    #     formatted_message += f"\n\nСтатус: {status}"
    
    return formatted_message