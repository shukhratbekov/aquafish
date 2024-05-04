from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, ReplyKeyboardBuilder, KeyboardButton

from configs import t


def get_main_buttons(titles, lang='ru'):
    builder = ReplyKeyboardBuilder()
    for title in titles:
        builder.button(text=title)
    builder.adjust(2)
    builder.row(KeyboardButton(text=f"📥 {t('Корзина', lang)}"), KeyboardButton(text=f"◀️ {t('Назад', lang)}"))
    markup = builder.as_markup()
    markup.resize_keyboard = True
    return markup


def get_quantity_buttons(quantity=1, lang='ru'):
    builder = InlineKeyboardBuilder()
    builder.button(text="-", callback_data="quantity_minus")
    builder.button(text=f"{quantity}", callback_data="quantity_number")
    builder.button(text="+", callback_data="quantity_plus")
    builder.button(text=f"📥 {t('Добавить в корзину', lang)}", callback_data='cart_add')
    builder.adjust(3)
    return builder.as_markup()


def get_cart_buttons(products, lang='ru'):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=f"🗑 {t('Очистить корзину', lang)}", callback_data="cart_clear"),
                InlineKeyboardButton(text=f"🚖 {t('Заказать', lang)}", callback_data="order"))
    for product in products:
        builder.row(InlineKeyboardButton(text=f"❌ {product[0]}", callback_data=f"clear_{product[1]}"))
    markup = builder.as_markup()
    return markup


def get_back_button(lang='ru'):
    builder = ReplyKeyboardBuilder()
    builder.button(text=f"◀️ {t('Назад', lang)}")
    markup = builder.as_markup()
    markup.resize_keyboard = True
    return markup


def get_phone_number_button(lang='ru'):
    builder = ReplyKeyboardBuilder()
    builder.button(text=f"📞 {t('Поделиться номером', lang)}", request_contact=True)
    builder.button(text=f"◀️ {t('Назад', lang)}")
    builder.adjust(1)
    markup = builder.as_markup()
    markup.resize_keyboard = True
    return markup


def get_shipping_buttons(lang='ru'):
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text=f"🛵 {t('Доставка', lang)}"), KeyboardButton(text=f"🚶 {t('Самовывоз', lang)}"))
    builder.row(KeyboardButton(text=f"◀️ {t('Назад', lang)}"))
    markup = builder.as_markup()
    markup.resize_keyboard = True
    return markup


def get_location_buttons(lang='ru'):
    builder = ReplyKeyboardBuilder()
    builder.button(text=f"📍 {t('Поделиться местоположением', lang)}", request_location=True)
    builder.button(text=f"◀️ {t('Назад', lang)}")
    builder.adjust(1)
    markup = builder.as_markup()
    markup.resize_keyboard = True
    return markup
