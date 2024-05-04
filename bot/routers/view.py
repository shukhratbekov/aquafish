from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from dals.view import ReviewDAL
from models.base import async_session

from models.user import TelegramUser

from keyboards.shop import get_back_button
from keyboards.start import get_menu_buttons

from configs import t

from utils import send_review

router = Router()


class ViewState(StatesGroup):
    view = State()


@router.message(F.text == "✍️ Оставить отзыв")
@router.message(F.text == f"✍️ {t('Оставить отзыв', 'uz')}")
async def view_handler(message: Message, state: FSMContext, tg_user: TelegramUser):
    await message.answer(f"{t('Напишите ваш отзыв', tg_user.language)}", reply_markup=get_back_button(tg_user.language))
    await state.set_state(ViewState.view)


@router.message(F.text == "◀️ Назад")
@router.message(F.text == f"◀️ {t('Назад', 'uz')}")
async def back_handler(message: Message, state: FSMContext, tg_user: TelegramUser):
    await message.answer(f"{t('Выберите действие', tg_user.language)}", reply_markup=get_menu_buttons(tg_user.language))
    await state.clear()


@router.message(ViewState.view)
async def get_view_handler(message: Message, state: FSMContext, tg_user: TelegramUser):
    text = message.text
    async with async_session() as session:
        review_dal = ReviewDAL(session)
        review_id = await review_dal.create_view(tg_user.id, text)
        await message.answer(f"{t('Ваш отзыв успешно отправлен', tg_user.language)}", reply_markup=get_menu_buttons(tg_user.language))
        await state.clear()
        await send_review(message, review_id, tg_user)
