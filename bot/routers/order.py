from aiogram import Router, F
from aiogram.types import Message

from dals.order import OrderDAL
from dals.shop import ProductDAL

from models.base import async_session
from models.user import TelegramUser

from configs import t

from utils import get_order_text, get_status

router = Router()


@router.message(F.text == '🛍 Мои заказы')
@router.message(F.text == f'🛍 {t("Мои заказы", "uz")}')
async def get_orders(message: Message, tg_user: TelegramUser):
    async with async_session() as session:
        order_dal = OrderDAL(session)
        orders = await order_dal.get_orders(tg_user.id)
        if not orders:
            await message.answer(f'{t("У вас нет заказов", tg_user.language)}')
        else:
            for order in orders:
                product_text = ''
                order_products = await order_dal.get_order_products(order_id=order.id)
                for order_product in order_products:
                    product_dal = ProductDAL(session)
                    product = await product_dal.get_product(tg_user.language, product_id=order_product.product_id)
                    product_text += f'<b>{product.title}</b>\n{order_product.quantity} ✖️ {product.price} = {product.price * order_product.quantity}\n'
                if order.shipping:
                    order_shipping = await order_dal.get_order_shipping(order.id)
                    order_shipping = order_shipping.address
                else:
                    order_shipping = f'{t("Самовывоз", tg_user.language)}'
                text = await get_order_text(order.id, get_status(order.status, tg_user.language), order_shipping,
                                            product_text, order.final_price,
                                            10000 if order.shipping else 0, tg_user.language)
                text += f"\n<b>{t('Дата Создания', tg_user.language)}:</b> {order.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
                await message.answer(text)
