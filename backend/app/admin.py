from django.contrib import admin
from django.utils.safestring import mark_safe
from parler.admin import TranslatableAdmin

from .models import Category, Product, TelegramUser, Order, OrderProduct, OrderShipping


@admin.register(Category)
class CategoryAdmin(TranslatableAdmin):
    list_display = ('title', 'parent', 'get_category_photo')
    list_per_page = 50
    list_filter = ('translations__created_at',)
    search_fields = ('translations__title',)
    order_by = ('created_at',)

    def get_category_photo(self, obj):
        if obj.photo:
            try:
                return mark_safe(f'<img src="{obj.photo.url}" width="75">')
            except Exception as e:
                return '-'


@admin.register(Product)
class ProductAdmin(TranslatableAdmin):
    list_display = ('title', 'price', 'category', 'is_active', 'get_product_photo')
    # list_editable = ('price', 'is_active')
    list_per_page = 50
    list_filter = ('translations__category', 'translations__is_active', 'translations__created_at')
    search_fields = ('translations__title',)
    order_by = ('created_at',)

    def get_product_photo(self, obj):
        if obj.photo:
            try:
                return mark_safe(f'<img src="{obj.photo.url}" width="75">')
            except Exception as e:
                return '-'


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name')
    list_per_page = 50
    # list_filter = ('created_at',)
    search_fields = ('first_name', 'last_name')
    order_by = ('created_at',)


class InlineOrderProductAdmin(admin.TabularInline):
    fk_name = 'order'
    model = OrderProduct
    extra = 0
    verbose_name = 'Продукт'
    verbose_name_plural = 'Продукты'


class InlineOrderShippingAdmin(admin.TabularInline):
    fk_name = 'order'
    model = OrderShipping
    extra = 0
    verbose_name = 'Доставка'
    verbose_name_plural = 'Доставка'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('pk', 'final_price', 'payment', 'status', 'shipping')
    list_per_page = 50
    list_editable = ('status', 'shipping')
    list_filter = ('created_at', 'payment', 'status', 'shipping')
    search_fields = ('pk',)
    order_by = ('created_at',)
    inlines = [InlineOrderProductAdmin, InlineOrderShippingAdmin]

    def get_inlines(self, request, obj):
        if obj and obj.shipping is not None:
            if obj.shipping:
                return [InlineOrderProductAdmin, InlineOrderShippingAdmin]
        return [InlineOrderProductAdmin]


