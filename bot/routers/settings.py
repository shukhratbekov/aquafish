from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

from configs import t
from dals.user import TelegramUserDAL
from keyboards.settings import get_settings_buttons
from keyboards.start import get_language_buttons, get_menu_buttons
from models.base import async_session
from models.user import TelegramUser

router = Router()

router.message.outer_middleware()


class LanguageState(StatesGroup):
    language = State()


@router.message(F.text == "◀️ Назад")
@router.message(F.text == f"◀️ {('Назад', 'uz')}")
async def back_handler(message: Message, state: FSMContext, tg_user: TelegramUser):
    await message.answer(f"{t('Выберите одно из следующих действий', tg_user.language)}",
                         reply_markup=get_menu_buttons(tg_user.language))
    await state.clear()


@router.message(F.text == "⚙️ Настройки")
@router.message(F.text == "⚙️ Sozlamalar")
async def settings_handler(message: Message, tg_user: TelegramUser):
    await message.answer(f"{t('Выберите действие', tg_user.language)}:", reply_markup=get_settings_buttons(tg_user.language))


@router.message(F.text == "Изменить язык")
@router.message(F.text == f"{t('Изменить язык', 'uz')}")
async def change_language_handler(message: Message, state: FSMContext, tg_user: TelegramUser):
    await message.answer(f"{t('Выберите язык', tg_user.language)}", reply_markup=get_language_buttons())
    await state.set_state(LanguageState.language)


@router.callback_query(LanguageState.language)
async def language_handler(callback: CallbackQuery, state: FSMContext, tg_user: TelegramUser):
    _, language = callback.data.split('_')
    async with async_session() as session:
        telegram_dal = TelegramUserDAL(session)
        await telegram_dal.update_language(tg_user.id, language=language)
        await callback.message.delete()
        await callback.answer(f"{t('Язык изменен', language)}")
        await callback.message.answer(f"{t('Выберите одно из следующих действий', language)}",
                                      reply_markup=get_menu_buttons(language),
                                      disable_notification=True)
        await state.clear()
