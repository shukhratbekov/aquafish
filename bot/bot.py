import os


from aiogram import Bot

from dotenv import load_dotenv

from aiogram import Dispatcher

load_dotenv()

TOKEN = os.getenv('TOKEN')

bot = Bot(token=TOKEN, parse_mode='HTML')


dp = Dispatcher()



