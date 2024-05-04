from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder, KeyboardButton

from configs import t


def get_language_buttons():
    builder = InlineKeyboardBuilder()
    builder.button(text="🇷🇺", callback_data="lang_ru")
    builder.button(text="🇺🇿", callback_data="lang_uz")
    builder.adjust(3)
    return builder.as_markup()


def get_menu_buttons(lang='ru'):
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text=f"🛒 {t('Каталог', lang)}"))
    builder.row(KeyboardButton(text=f"🛍 {t('Мои заказы', lang)}"))
    builder.row(KeyboardButton(text=f"✍️ {t('Оставить отзыв', lang)}"),
                KeyboardButton(text=f"⚙️ {t('Настройки', lang)}"))
    markup = builder.as_markup()
    markup.resize_keyboard = True
    return markup
