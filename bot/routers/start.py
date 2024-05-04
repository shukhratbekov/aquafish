from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

from keyboards.start import get_menu_buttons
from models.user import TelegramUser

from configs import t

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message, tg_user: TelegramUser):
    print(tg_user.language)
    await message.answer(f"{t('Выберите одно из следующих действий', lang=tg_user.language)}",
                         reply_markup=get_menu_buttons(tg_user.language))

# @router.message(F.text == '◀️ Назад')
# async def back_handler(message: Message, tg_user: TelegramUser):
#     await message.answer("Выберите одно из следующих действий", reply_markup=get_menu_buttons())
