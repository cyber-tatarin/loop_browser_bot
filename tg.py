import telebot
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# Replace 'YOUR_API_TOKEN' with the actual API token you obtained from BotFather
API_TOKEN = os.getenv('TG_API_TOKEN')

# Create a Bot instance
bot = telebot.TeleBot(token=API_TOKEN)

# Replace 'CHAT_ID' with the chat ID of the user, group, or channel you want to send the message to
CHAT_ID = '459471362'


def send_message(message):
    bot.send_message(chat_id=CHAT_ID, text=message)
