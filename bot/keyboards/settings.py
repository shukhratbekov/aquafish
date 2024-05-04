from aiogram.utils.keyboard import ReplyKeyboardBuilder, KeyboardButton

from configs import t


def get_settings_buttons(lang='ru'):
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text=f"{t('Изменить язык', lang)}"))
    builder.row(KeyboardButton(text=f"◀️ {t('Назад', lang)}"))
    markup = builder.as_markup()
    markup.resize_keyboard = True
    return markup
