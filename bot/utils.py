from aiogram.types import Message
from aiogram.utils.formatting import HashTag

from dals.order import OrderDAL
from dals.shop import ProductDAL, CartDAL

from geopy import Nominatim

from dals.user import TelegramUserDAL
from dals.view import ReviewDAL
from models.base import async_session

from models.user import TelegramUser

from configs import t

nom = Nominatim(user_agent='008')


async def get_geocode(latitude, longitude):
    address = nom.reverse((latitude, longitude), exactly_one=True)
    return str(address)


async def get_order_text(order_id, status, shipping, products, total_price, shipping_price, lang):
    text = f'<b>{t('Заказ', lang)}:</b> #{order_id}\n<b>{t('Статус', lang)}:</b> {status}\n<b>{t('Доставка', lang)}:</b> {shipping}\n\n'
    text += products
    text += f'\n<b>{t('Товары', lang)}: </b>{total_price} {t('сум', lang)}\n<b>{t('Доставка', lang)}: </b> {shipping_price} {t('сум', lang)}\n<b>{t('Итого', lang)}: </b> {total_price + shipping_price} {t('сум', lang)}\n'
    return text


async def get_user(telegram_id):
    async with async_session() as session:
        user_dal = TelegramUserDAL(session)
        user = await user_dal.get_user(telegram_id)
        return user


async def create_user(telegram_id, first_name, last_name, language, username=None):
    async with async_session() as session:
        user_dal = TelegramUserDAL(session)
        await user_dal.create_user(
            telegram_id=telegram_id,
            first_name=first_name,
            last_name=last_name,
            username=username,
            language=language
        )


async def get_or_create_user(telegram_id, first_name, last_name, language, username=None):
    user = await get_user(telegram_id)
    if user:
        return user
    await create_user(telegram_id, first_name, last_name, language, username)
    return await get_user(telegram_id)


async def create_cart(user_id):
    async with async_session() as session:
        cart_dal = CartDAL(session)
        await cart_dal.create_cart(user_id)


async def get_cart(user_id):
    async with async_session() as session:
        cart_dal = CartDAL(session)
        cart = await cart_dal.get_cart(user_id)
        return cart


async def get_or_create_cart(user_id):
    cart = await get_cart(user_id)
    if cart:
        return cart
    await create_cart(user_id)
    return await get_cart(user_id)


async def send_order(message: Message, order_id: int, tg_user: TelegramUser):
    async with async_session() as session:

        order_dal = OrderDAL(session)
        order = await order_dal.get_order(order_id)
        order_products = await order_dal.get_order_products(order_id)
        text = f"<b>Заказ:</b> #{order_id}\n<b>Клиент: </b>{tg_user.first_name} {tg_user.last_name}\n"
        text += f"<b>Телефон: </b>{order.phone_number}\n"
        text += f"<b>Дата Создания:</b> {order.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        total_price = 0
        products_text = ''
        for order_product in order_products:
            product_dal = ProductDAL(session)
            product = await product_dal.get_product('ru', order_product.product_id)
            products_text += f'<b>{product.title}</b>\n'
            products_text += f'{order_product.quantity} ✖️ {product.price} = {product.price * order_product.quantity}\n'
            total_price += product.price * order_product.quantity
        if order.shipping:
            order_shipping = await order_dal.get_order_shipping(order_id)
            text += f"<b>Доставка: </b>{order_shipping.address}\n\n"
            text += products_text
            text += f"<b>Общая сумма: </b>{total_price} сум\n<b>Доставка:</b> 10000 сум\n<b>Итого:</b> {total_price + 10000}сум"
            await message.bot.send_message(650475665, text)
            await message.bot.send_location(650475665, order_shipping.latitude, order_shipping.longitude)
        else:
            text += f"<b>Доставка: </b>Самовывоз\n"
            text += products_text
            text += f"<b>Общая сумма: </b>{total_price} сум\n<b>Доставка:</b> 0 сум\n<b>Итого:</b> {total_price}сум"
            await message.bot.send_message(650475665, text)


async def send_review(message: Message, review_id, tg_user: TelegramUser):
    async with async_session() as session:
        review_dal = ReviewDAL(session)
        review = await review_dal.get_view(review_id)
        text = f"<b>Отзыв:</b> #{review.id}\n<b>Клиент: </b>{tg_user.first_name} {tg_user.last_name}\n\n {review.view}"
        await message.bot.send_message(650475665, text)


async def create_order(user_id, phone_number, shipping, status, payment, final_price):
    async with async_session() as session:
        order_dal = OrderDAL(session)
        order_id = await order_dal.create_order(
            telegram_user_id=user_id,
            phone_number=phone_number,
            shipping=shipping,
            status=status,
            payment=payment,
            final_price=final_price
        )
    return order_id


async def create_order_products(order_id, language, cart_products):
    async with async_session() as session:
        order_product_dal = OrderDAL(session)
        product_text = ''
        for cart_product in cart_products:
            async with async_session() as product_session:
                product = await ProductDAL(product_session).get_product(language, cart_product.product_id)
                await order_product_dal.create_order_product(
                    order_id=order_id,
                    product_id=cart_product.product_id,
                    quantity=cart_product.quantity,
                    price=product.price
                )
                product_text += f'<b>{product.title}</b>\n{cart_product.quantity} ✖️ {product.price} = {product.price * cart_product.quantity}\n'
        return product_text


async def create_order_shipping(order_id, geocode, longitude, latitude):
    async with async_session() as session:
        order_dal = OrderDAL(session)
        await order_dal.create_order_shipping(
            order_id=order_id,
            address=geocode,
            longitude=longitude,
            latitude=latitude
        )


def get_status(status, lang):
    if status == 'process':
        return t('В процессе', lang)
    elif status == 'canceled':
        return t('Отменен', lang)
    elif status == 'completed':
        return t('Завершен', lang)
