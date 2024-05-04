import json
import time

from translate import Translator

translator = Translator(to_lang="uz", from_lang="ru")

hell = translator.translate("Назад")
print(hell)


def t(text: str, lang: str):
    translator = Translator(to_lang=lang, from_lang="ru")
    result = ''.join(translator.translate(text).split(' & # 160;'))
    return result

print(t("Заказать", "uz"))

words = \
    [
        "Выберите язык", "Выберите действие:", "Язык изменен", "Выберите язык", "Выберите одно из следующих действий",
        "Выберите одно из следующих действий", "Напишите ваш отзыв", "Ваш отзыв успешно отправлен", "У вас нет заказов",
        "Самовывоз", "В процессе", "Выберите категорию", "Ваша корзина пуста", "Общая Сумма", "сум", "Корзина очищена",
        "Выберите подкатегорию", "Выберите продукт", "В данной категории нет продуктов",
        "Вы не выбрали категорию попробуйте еще раз", "Вы не выбрали подкатегорию попробуйте еще раз",
        "Цена", "Товар добавлен в корзину", "Оформим еще заказы",
        "Отправьте номер телефона в таком формате +998 ** *** ** **",
        "Выберите тип заказа",
        "Вы ввели номер телефона в неправильном формате. Пожалуйста, отправьте или введите заново",
        "Отправьте геолокацию", "Вы ввели неправильное действие. Выберите тип заказа",
        "Вы не отправили локацию. Отправьте локацию",
        "Доставка", "Общая сумма", "Итого", "Самовывоз", "Отзыв", "Клиент", "Дата Создания", "Телефон", "Заказ",
        "Товары",
        "Статус", "Каталог", "Мои заказы", "Оставить отзыв", "Настройки", "Изменить язык", "Назад", "Корзина",
        "Добавить в корзину"
        "Заказать", "Очистить корзину", "Поделиться номером", "Поделиться местоположением"
    ]


def generate_translation_dict(words):
    translation_dict = {'ru': {}, 'uz': {}}

    # Iterate through each word in the list
    for word in words:
        # Translate the word from Russian to Uzbek
        translator_ru_to_uz = Translator(to_lang="uz", from_lang="ru")
        translated_word_uz = translator_ru_to_uz.translate(word)

        # Store translations in the dictionary
        translation_dict['ru'][word] = word
        translation_dict['uz'][word] = translated_word_uz

    return translation_dict
# translation_dict = generate_translation_dict(words)
#
# # Save translation dictionary to a JSON file
# with open('translation_dict.json', 'w', encoding='utf-8') as f:
#     json.dump(translation_dict, f, ensure_ascii=False, indent=4)
#
# print("Translation dictionary saved to translation_dict.json")