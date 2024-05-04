from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from utils import get_or_create_cart, get_or_create_user

from typing import Dict, Callable, Awaitable, Any


class AuthMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        user = data.get('event_from_user')
        tg_user = await get_or_create_user(
            telegram_id=user.id,
            first_name=user.first_name if user.first_name else 'None',
            last_name=user.last_name if user.last_name else 'None',
            username=user.username,
            language=user.language_code if user.language_code in ['ru', 'en', 'uz'] else 'ru',
        )
        cart = await get_or_create_cart(tg_user.id)
        data['cart'] = cart
        data['tg_user'] = tg_user
        return await handler(event, data)
