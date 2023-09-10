import telebot
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# Replace 'YOUR_API_TOKEN' with the actual API token you obtained from BotFather
API_TOKEN = os.getenv('TG_API_TOKEN')

# Create a Bot instance
bot = telebot.TeleBot(token=API_TOKEN)

# Replace 'CHAT_ID' with the chat ID of the user, group, or channel you want to send the message to
CHAT_IDS = ['459471362', '962646747']


def send_message(message):
    for chat_id in CHAT_IDS:
        try:
            bot.send_message(chat_id=chat_id, text=message)
        except Exception:
            pass
    