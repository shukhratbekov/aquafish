import re

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

from dals.shop import CategoryDAL, ProductDAL, CartDAL

from keyboards.shop import *
from keyboards.start import get_menu_buttons

from models.base import async_session
from models.cart import Cart
from models.user import TelegramUser

from configs import t

from utils import get_geocode, get_order_text, send_order, create_order, create_order_products, create_order_shipping, \
    get_status

router = Router()

phone_regex = re.compile(r'^\+998(\s\d{2}\s\d{3}\s\d{2}\s\d{2}|\d{9})$')


class ShopState(StatesGroup):
    category = State()
    subcategory = State()
    product = State()
    quantity = State()


class CartState(StatesGroup):
    action = State()


class OrderState(StatesGroup):
    phone_number = State()
    shipping = State()
    location = State()


@router.message(F.text == "🛒 Каталог")
@router.message(F.text == f"🛒 {t("Каталог", "uz")}")
async def catalog_handler(message: Message, state: FSMContext, tg_user: TelegramUser, cart: Cart):
    async with async_session() as session:
        category_dal = CategoryDAL(session)
        categories = await category_dal.get_categories(tg_user.language)
        category_titles = [category.title for category in categories]
        await message.answer(f"{t("Выберите категорию", tg_user.language)}",
                             reply_markup=get_main_buttons(category_titles, tg_user.language))
        await state.set_state(ShopState.category)


@router.message(F.text == "📥 Корзина")
@router.message(F.text == f"📥 {t("Корзина", "uz")}")
async def cart_handler(message: Message, state: FSMContext, tg_user: TelegramUser, cart: Cart):
    async with async_session() as session:
        cart_dal = CartDAL(session)
        cart_products = await cart_dal.get_cart_products(cart.id)
        if not cart_products:
            await message.answer(f"{t("Ваша корзина пуста", tg_user.language)}")
            category_dal = CategoryDAL(session)
            categories = await category_dal.get_categories(tg_user.language)
            category_titles = [category.title for category in categories]
            await message.answer(f"{t("Выберите категорию", tg_user.language)}",
                                 reply_markup=get_main_buttons(category_titles, tg_user.language))
            await state.set_state(ShopState.category)
        else:
            text = f"<b>{t("Ваша Корзина", tg_user.language)}:</b>\n"
            total_price = 0
            cart_product_titles = []
            cart_product_ids = []
            for cart_product in cart_products:
                cart_product_ids.append(cart_product.id)
                product_dal = ProductDAL(session)
                product = await product_dal.get_product(tg_user.language, cart_product.product_id)
                text += f"{cart_product.quantity} ✖️ {product.title}\n"
                cart_product_titles.append([product.title, cart_product.product_id])
                total_price += cart_product.quantity * product.price
            text += f"<b>{t("Общая Сумма", tg_user.language)}:</b> {total_price} {t("сум", tg_user.language)}"
            await message.answer(t("Выберите действие", tg_user.language),
                                 reply_markup=get_back_button(tg_user.language))
            await message.answer(text, reply_markup=get_cart_buttons(cart_product_titles, tg_user.language))
            await state.set_state(CartState.action)


@router.callback_query(F.data.startswith("cart"), CartState.action)
async def cart_clear_handler(call: CallbackQuery, state: FSMContext, tg_user: TelegramUser, cart: Cart):
    async with async_session() as session:
        cart_dal = CartDAL(session)
        await cart_dal.clear_cart(cart.id)
        await call.message.delete()
        await call.message.answer(t("Корзина очищена", tg_user.language),
                                  reply_markup=get_menu_buttons(tg_user.language))
        await state.clear()


@router.callback_query(F.data.startswith("clear"), CartState.action)
async def cart_product_handler(call: CallbackQuery, state: FSMContext, tg_user: TelegramUser, cart: Cart):
    _, cart_product_id = call.data.split("_")
    async with async_session() as session:
        cart_dal = CartDAL(session)
        await cart_dal.remove_product_from_cart(cart.id, int(cart_product_id))
        cart_products = await cart_dal.get_cart_products(cart.id)
        cart_product_titles = []
        if not cart_products:
            await call.message.delete()
            await state.clear()
            await call.message.answer(t("Ваша корзина пуста", tg_user.language),
                                      reply_markup=get_menu_buttons(tg_user.language))
        else:
            for cart_product in cart_products:
                product_dal = ProductDAL(session)
                product = await product_dal.get_product(tg_user.language, cart_product.product_id)
                cart_product_titles.append([product.title, cart_product.id])
            await call.message.edit_reply_markup(reply_markup=get_cart_buttons(cart_product_titles, tg_user.language))
            await state.set_state(CartState.action)


@router.message(F.text == "◀️ Назад", CartState.action)
@router.message(F.text == f"◀️ {t("Назад", "uz")}", CartState.action)
async def cart_back_category_handler(message: Message, state: FSMContext, tg_user: TelegramUser, cart: Cart):
    async with async_session() as session:
        category_dal = CategoryDAL(session)
        categories = await category_dal.get_categories(tg_user.language)
        category_titles = [category.title for category in categories]
        await message.answer(t("Выберите категорию", tg_user.language),
                             reply_markup=get_main_buttons(category_titles, tg_user.language))
        await state.set_state(ShopState.category)


@router.message(F.text == "◀️ Назад", ShopState.category)
@router.message(F.text == f"◀️ {t("Назад", "uz")}", ShopState.category)
async def back_handler(message: Message, state: FSMContext, tg_user: TelegramUser, cart: Cart):
    await message.answer(t("Выберите одно из следующих действий", tg_user.language),
                         reply_markup=get_menu_buttons(tg_user.language))
    await state.clear()


@router.message(ShopState.category)
async def category_handler(message: Message, state: FSMContext, tg_user: TelegramUser, cart: Cart):
    category_title = message.text
    async with async_session() as session:
        category_dal = CategoryDAL(session)
        category = await category_dal.get_category_by_title(category_title)
        if category:
            text = f"<b>{category.title}</b>\n{category.description}"
            if category.photo:
                pass
            else:
                await message.answer(text)
            subcategories = await category_dal.get_subcategories(tg_user.language, category.master_id)
            if subcategories:
                subcategories_title = [subcategory.title for subcategory in subcategories]
                await message.answer(t("Выберите подкатегорию", tg_user.language),
                                     reply_markup=get_main_buttons(subcategories_title, tg_user.language))
                await state.update_data(category=category.master_id)
                await state.set_state(ShopState.subcategory)
            else:
                product_dal = ProductDAL(session)
                products = await product_dal.get_products(tg_user.language, category.master_id)
                if products:
                    products_title = [product.title for product in products]
                    await state.update_data(category=category.master_id, subcategory=None)
                    await message.answer(t("Выберите продукт", tg_user.language),
                                         reply_markup=get_main_buttons(products_title, tg_user.language))
                    await state.set_state(ShopState.product)
                else:
                    categories = await category_dal.get_categories(tg_user.language)
                    category_titles = [category.title for category in categories]
                    await message.answer(t("В данной категории нет продуктов", tg_user.language),
                                         reply_markup=get_main_buttons(category_titles, tg_user.language))
                    await state.set_state(ShopState.category)
        else:
            await message.answer(t("Вы не выбрали категорию попробуйте еще раз", tg_user.language))
            await state.set_state(ShopState.category)


@router.message(F.text == "◀️ Назад", ShopState.subcategory)
@router.message(F.text == f"◀️ {t("Назад", "uz")}", ShopState.subcategory)
async def back_category_handler(message: Message, state: FSMContext, tg_user: TelegramUser, cart: Cart):
    async with async_session() as session:
        category_dal = CategoryDAL(session)
        categories = await category_dal.get_categories(tg_user.language)
        category_titles = [category.title for category in categories]
        await message.answer(t("Выберите категорию", tg_user.language),
                             reply_markup=get_main_buttons(category_titles, tg_user.language))
        await state.set_state(ShopState.category)


@router.message(ShopState.subcategory)
async def subcategory_handler(message: Message, state: FSMContext, tg_user: TelegramUser, cart: Cart):
    subcategory_title = message.text
    async with async_session() as session:
        category_dal = CategoryDAL(session)
        subcategory = await category_dal.get_category_by_title(subcategory_title)
        if subcategory:
            text = f"<b>{subcategory.title}</b>\n{subcategory.description}"
            if subcategory.photo:
                pass
            else:
                await message.answer(text)
            product_dal = ProductDAL(session)
            products = await product_dal.get_products(tg_user.language, subcategory.master_id)
            if products:
                products_title = [product.title for product in products]
                await state.update_data(subcategory=subcategory.master_id)
                await message.answer(t("Выберите продукт", tg_user.language),
                                     reply_markup=get_main_buttons(products_title, tg_user.language))
                await state.set_state(ShopState.product)
            else:
                data = await state.get_data()
                category_id = data['category']
                subcategories = await category_dal.get_subcategories(tg_user.language, category_id)
                subcategories_title = [subcategory.title for subcategory in subcategories]
                await message.answer(t("В данной категории нет продуктов", tg_user.language),
                                     reply_markup=get_main_buttons(subcategories_title, tg_user.language))
                await state.set_state(ShopState.subcategory)
        else:
            data = await state.get_data()
            category_id = data['category']
            subcategories = await category_dal.get_subcategories(tg_user.language, category_id)
            subcategories_title = [subcategory.title for subcategory in subcategories]
            await message.answer(t("Вы не выбрали подкатегорию попробуйте еще раз", tg_user.language),
                                 reply_markup=get_main_buttons(subcategories_title, tg_user.language))
            await state.set_state(ShopState.subcategory)


@router.message(F.text == "◀️ Назад", ShopState.product)
@router.message(F.text == f"◀️ {t("Назад", "uz")}", ShopState.product)
async def back_subcategory_handler(message: Message, state: FSMContext, tg_user: TelegramUser, cart: Cart):
    data = await state.get_data()
    subcategory_id = data['subcategory']
    category_id = data['category']
    async with async_session as session:
        category_dal = CategoryDAL(session)
        if subcategory_id:
            subcategories = await category_dal.get_subcategories(tg_user.language, category_id)
            subcategories_title = [subcategory.title for subcategory in subcategories]
            await message.answer(t("Выберите подкатегорию", tg_user.language),
                                 reply_markup=get_main_buttons(subcategories_title, tg_user.language))
            await state.set_state(ShopState.subcategory)
        else:
            categories = await category_dal.get_categories(tg_user.language)
            category_titles = [category.title for category in categories]
            await message.answer(t("Выберите категорию", tg_user.language),
                                 reply_markup=get_main_buttons(category_titles, tg_user.language))
            await state.clear()
            await state.set_state(ShopState.category)


@router.message(ShopState.product)
async def product_handler(message: Message, state: FSMContext, tg_user: TelegramUser, cart: Cart):
    async with async_session() as session:
        product_dal = ProductDAL(session)
        product = await product_dal.get_product_by_title(message.text)
        if product:
            if product.photo:
                # TODO: Временно пока на сервер не залью
                text = f'<b>{product.title}</b>\n\n{product.description}\n<b>{t('Цена', tg_user.language)}:</b>{product.price}'
                await message.answer(text, reply_markup=get_quantity_buttons(lang=tg_user.language))
                await state.update_data(product=product.master_id)
                await state.update_data(quantity=1)
                await state.set_state(ShopState.quantity)
            else:
                text = f'<b>{product.title}</b>\n\n{product.description}\n<b>{t('Цена', tg_user.language)}:</b>{product.price}'
                await message.answer(text, reply_markup=get_quantity_buttons(lang=tg_user.language))
                await state.update_data(product=product.master_id)
                await state.update_data(quantity=1)
                await state.set_state(ShopState.quantity)
        else:
            data = await state.get_data()
            subcategory_id = data['subcategory']
            products = await product_dal.get_products(tg_user.language, subcategory_id)
            products_title = [product.title for product in products]
            await message.answer(t("Вы не выбрали продукт попробуйте еще раз", tg_user.language),
                                 get_main_buttons(products_title, tg_user.language))
            await state.set_state(ShopState.product)


@router.message(F.text == "◀️ Назад", ShopState.quantity)
@router.message(F.text == f"◀️ {t("Назад", "uz")}", ShopState.quantity)
async def back_product_handler(message: Message, state: FSMContext, tg_user: TelegramUser, cart: Cart):
    data = await state.get_data()
    category_id = data['category']
    subcategory_id = data['subcategory']
    async with async_session as session:
        product_dal = ProductDAL(session)
        if subcategory_id:
            products = await product_dal.get_products(tg_user.language, subcategory_id)
        else:
            products = await product_dal.get_products(tg_user.language, category_id)
        products_titles = [product.title for product in products]
        await message.delete()
        await message.answer(t("Выберите продукт", tg_user.language),
                             reply_markup=get_main_buttons(products_titles, tg_user.language))
        await state.clear()
        await state.update_data(category=category_id, subcategory=subcategory_id)
        await state.set_state(ShopState.product)


@router.callback_query(F.data.startswith('quantity'), ShopState.quantity)
async def quantity_handler(call: CallbackQuery, state: FSMContext, tg_user: TelegramUser, cart: Cart):
    _, action = call.data.split('_')
    data = await state.get_data()
    quantity = int(data['quantity'])
    if action == 'minus':
        if quantity <= 1:
            await call.answer(f"{quantity}")
            await state.set_state(ShopState.quantity)
        else:
            quantity -= 1
            await state.update_data(quantity=str(quantity))
            await call.message.edit_reply_markup(reply_markup=get_quantity_buttons(quantity, tg_user.language))
            await call.answer(f"{quantity}")
            await state.set_state(ShopState.quantity)
    elif action == 'plus':
        quantity += 1
        await state.update_data(quantity=str(quantity))
        await call.message.edit_reply_markup(reply_markup=get_quantity_buttons(quantity, tg_user.language))
        await call.answer(f"{quantity}")
        await state.set_state(ShopState.quantity)
    elif action == 'number':
        await call.answer(str(quantity))
        await call.answer(f"{quantity}")
        await state.set_state(ShopState.quantity)


@router.callback_query(F.data.startswith("cart"), ShopState.quantity)
async def add_to_cart_handler(call: CallbackQuery, state: FSMContext, tg_user: TelegramUser, cart: Cart):
    async with async_session() as session:
        cart_dal = CartDAL(session=session)
        data = await state.get_data()
        product_id = data["product"]
        quantity = data["quantity"]
        await call.message.delete()
        await cart_dal.add_product_to_cart(cart.id, product_id, int(quantity))
        await call.answer(t("Товар добавлен в корзину", tg_user.language))
        category_dal = CategoryDAL(session)
        categories = await category_dal.get_categories(tg_user.language)
        category_titles = [category.title for category in categories]
        await call.message.answer(t("Оформим еще заказы", tg_user.language),
                                  reply_markup=get_main_buttons(category_titles, tg_user.language))
        await state.clear()
        await state.set_state(ShopState.category)


# <--------------------------------------------- Order Handlers ------------------------------------------------------->

@router.callback_query(F.data.startswith("order"), CartState.action)
async def start_order_handler(call: CallbackQuery, state: FSMContext, tg_user: TelegramUser, cart: Cart):
    await call.message.answer(t("Отправьте номер телефона в таком формате +998 ** *** ** **", tg_user.language),
                              reply_markup=get_phone_number_button(tg_user.language))
    await state.set_state(OrderState.phone_number)


@router.message(F.text == "◀️ Назад", OrderState.phone_number)
@router.message(F.text == f"◀️ {t("Назад", "uz")}", OrderState.phone_number)
async def back_order_handler(message: Message, state: FSMContext, tg_user: TelegramUser, cart: Cart):
    async with async_session() as session:
        category_dal = CategoryDAL(session)
        categories = await category_dal.get_categories(tg_user.language)
        category_titles = [category.title for category in categories]
        await message.answer(t("Выберите категорию", tg_user.language),
                             reply_markup=get_main_buttons(category_titles, tg_user.language))
        await state.set_state(ShopState.category)


@router.message(OrderState.phone_number)
async def phone_number_handler(message: Message, state: FSMContext, tg_user: TelegramUser, cart: Cart):
    if (message.text and phone_regex.match(message.text)) or message.contact:
        phone_number = message.text if message.text else message.contact.phone_number
        await state.update_data(phone_number=phone_number)
        await message.answer(t("Выберите тип заказа", tg_user.language),
                             reply_markup=get_shipping_buttons(tg_user.language))
        await state.set_state(OrderState.shipping)
    else:
        await message.answer(
            t("Вы ввели номер телефона в неправильном формате. Пожалуйста, отправьте или введите заново",
              tg_user.language),
            reply_markup=get_phone_number_button(tg_user.language))
        await state.set_state(OrderState.phone_number)


@router.message(F.text == "◀️ Назад", OrderState.shipping)
@router.message(F.text == f"◀️ {t("Назад", 'uz')}", OrderState.shipping)
async def back_phone_number_handler(message: Message, state: FSMContext, tg_user: TelegramUser, cart: Cart):
    await message.answer(t("Отправьте номер телефона в таком формате +998 ** *** ** **", tg_user.language),
                         reply_markup=get_phone_number_button(tg_user.language))
    await state.set_state(OrderState.phone_number)


# ======================================================================================================================

@router.message(OrderState.shipping)
async def shipping_handler(message: Message, state: FSMContext, tg_user: TelegramUser, cart: Cart):
    shipping = message.text
    if shipping == f'🛵 {t("Доставка", tg_user.language)}':
        await message.answer(t("Отправьте геолокацию", tg_user.language),
                             reply_markup=get_location_buttons(tg_user.language))
        await state.update_data(shipping=True)
        await state.set_state(OrderState.location)
    elif shipping == f'🚶 {t("Самовывоз", tg_user.language)}':
        data = await state.get_data()
        async with async_session() as cart_session:
            cart_dal = CartDAL(cart_session)
            cart_products = await cart_dal.get_cart_products(cart.id)
            if cart_products:
                total_price = await cart_dal.get_total_price(cart.id)
                status = 'process'
                order_id = await create_order(tg_user.id, data['phone_number'], False, status, 'cash', total_price)
                product_text = await create_order_products(order_id, tg_user.language, cart_products)
                text = await get_order_text(order_id, get_status(status, tg_user.language), shipping, product_text,
                                            total_price, 0, tg_user.language)
                await message.answer(text)
                await send_order(message, order_id, tg_user)
                await message.answer(f"{t("Оформим еще заказы", tg_user.language)}?",
                                     reply_markup=get_menu_buttons(tg_user.language))
                await state.clear()
                await cart_dal.clear_cart(cart.id)
            else:
                await message.answer(t("Ваша корзина пуста", tg_user.language),
                                     reply_markup=get_menu_buttons(tg_user.language))
                await state.clear()
    else:
        await message.answer(t("Вы ввели неправильное действие. Выберите тип заказа", tg_user.language),
                             reply_markup=get_shipping_buttons(tg_user.language))
        await state.set_state(OrderState.shipping)


@router.message(F.text == "◀️ Назад", OrderState.location)
@router.message(F.text == f"◀️ {t("Назад", "uz")}", OrderState.location)
async def back_shipping_handler(message: Message, state: FSMContext, tg_user: TelegramUser, cart: Cart):
    await message.answer(t("Выберите тип заказа", tg_user.language),
                         reply_markup=get_shipping_buttons(tg_user.language))
    await state.set_state(OrderState.shipping)


@router.message(OrderState.location)
async def location_handler(message: Message, state: FSMContext, tg_user: TelegramUser, cart: Cart):
    if message.location:
        latitude = message.location.latitude
        longitude = message.location.longitude
        geocode = await get_geocode(latitude, longitude)
        await state.update_data(location=geocode)
        data = await state.get_data()
        async with async_session() as session:
            cart_dal = CartDAL(session)
            cart_products = await cart_dal.get_cart_products(cart.id)
            if cart_products:
                total_price = await cart_dal.get_total_price(cart.id)
                status = 'process'
                order_id = await create_order(tg_user.id, data['phone_number'], True, status, 'cash', total_price)
                product_text = await create_order_products(order_id, tg_user.language, cart_products)

                await create_order_shipping(order_id, geocode, longitude, latitude)
                text = await get_order_text(order_id, get_status(status, tg_user.language), geocode, product_text,
                                            total_price, 10000, tg_user.language)

                await message.answer(text)
                await send_order(message, order_id, tg_user)
                await message.answer(f"{t("Оформим еще заказы", tg_user.language)}?",
                                     reply_markup=get_menu_buttons(tg_user.language))
                await state.clear()
                await cart_dal.clear_cart(cart.id)
            else:
                await message.answer(f"{t("Ваша корзина пуста", tg_user.language)}",
                                     reply_markup=get_menu_buttons(tg_user.language))
                await state.clear()
    else:
        await message.answer(t("Вы не отправили локацию. Отправьте локацию", tg_user.language),
                             reply_markup=get_location_buttons(tg_user.language))
        await state.set_state(OrderState.location)
