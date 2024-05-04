import os

from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from parler.models import TranslatableModel, TranslatedFields


class Category(TranslatableModel):
    translations = TranslatedFields(
        title=models.CharField(max_length=256, verbose_name="Название Категории"),
        description=models.TextField(null=True, blank=True, verbose_name="Описание Категории"),
        photo=models.ImageField(upload_to="categories/", null=True, blank=True, verbose_name="Фото"),

        created_at=models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    )
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, verbose_name='Категория',
                               related_name='subcategories')

    def __str__(self):
        return self.title

    def get_image(self):
        if self.photo:
            return self.photo.url
        else:
            return 'https://avatars.mds.yandex.net/get-mpic/4614963/img_id1492585197771787400.jpeg/600x800'

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Product(TranslatableModel):
    translations = TranslatedFields(
        title=models.CharField(max_length=256, verbose_name="Название Товара"),
        description=models.TextField(null=True, blank=True, verbose_name="Описание Товара"),
        photo=models.ImageField(upload_to="products/", null=True, blank=True, verbose_name="Фото"),
        category=models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name='Категория'),
        price=models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена'),
        is_active=models.BooleanField(default=True, verbose_name='Активен'),
        created_at=models.DateTimeField(auto_now_add=True, verbose_name="Дата Создания")
    )

    def get_image(self):
        if self.photo:
            return self.photo.url
        else:
            return 'https://avatars.mds.yandex.net/get-mpic/4614963/img_id1492585197771787400.jpeg/600x800'

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'


@receiver(pre_delete, sender=Product)
def delete_product_image(sender, instance, **kwargs):
    # Проверяем, есть ли у продукта изображение
    if instance.photo:
        # Получаем путь к файлу изображения
        image_path = instance.photo.path
        # Удаляем файл изображения
        if os.path.exists(image_path):
            os.remove(image_path)


@receiver(pre_delete, sender=Category)
def delete_category_image(sender, instance, **kwargs):
    # Проверяем, есть ли у продукта изображение
    if instance.photo:
        # Получаем путь к файлу изображения
        image_path = instance.photo.path
        # Удаляем файл изображения
        if os.path.exists(image_path):
            os.remove(image_path)


class TelegramUser(models.Model):
    LANGUAGE_CHOICES = (
        ('ru', 'Русский'),
        ('uz', 'Узбекский'),
    )
    telegram_id = models.BigIntegerField(unique=True, verbose_name="Telegram ID")
    first_name = models.CharField(max_length=256, verbose_name="Имя")
    last_name = models.CharField(max_length=256, verbose_name="Фамилия")
    username = models.CharField(max_length=256, null=True, blank=True, verbose_name="Username")
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, verbose_name='Язык Пользователя')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата Создания")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = 'Пользователь Telegram'
        verbose_name_plural = 'Пользователи Telegram'


class Cart(models.Model):
    telegram_user = models.OneToOneField(TelegramUser, on_delete=models.CASCADE, verbose_name="Клиент")


class CartProduct(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, verbose_name="Корзина")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")


class Order(models.Model):
    PAYMENT_TYPE = (
        ('cash', 'Наличными'),
        ('card', 'Картой'),
    )
    ORDER_STATUS = (
        ('process', 'В Процессе'),
        ('canceled', 'Отменен'),
        ('completed', 'Выполнен'),
    )
    final_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Общая сумма")
    telegram_user = models.ForeignKey(TelegramUser, on_delete=models.SET_NULL, null=True, blank=True,
                                      verbose_name="Клиент")
    payment = models.CharField(max_length=10, choices=PAYMENT_TYPE, verbose_name="Оплата")
    phone_number = models.CharField(max_length=128, verbose_name="Номер Телефона Клиента")
    status = models.CharField(max_length=10, choices=ORDER_STATUS, verbose_name="Статус заказа")
    shipping = models.BooleanField(default=False, verbose_name="Доставка")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата Создания")

    def __str__(self):
        return f"{self.telegram_user.first_name} {self.telegram_user.last_name}"

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name="Заказ")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Товар")
    quantity = models.PositiveIntegerField(verbose_name="Количество")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")

    def __str__(self):
        return f"{self.order.pk} {self.product.title} {self.quantity}"

    class Meta:
        verbose_name = 'Товар в заказе'
        verbose_name_plural = 'Товары в заказе'


class OrderShipping(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, verbose_name="Заказ")
    address = models.CharField(max_length=256, verbose_name="Адрес доставки")
    longitude = models.FloatField(verbose_name="Долгота")
    latitude = models.FloatField(verbose_name="Широта")

    def __str__(self):
        return f"{self.order.pk} {self.address}"

    class Meta:
        verbose_name = 'Доставка'
        verbose_name_plural = 'Доставки'


class Review(models.Model):
    telegram_user = models.ForeignKey(TelegramUser, on_delete=models.SET_NULL, null=True, blank=True,
                                      verbose_name="Клиент")
    view = models.TextField(verbose_name='Отзыв')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата Создания")
