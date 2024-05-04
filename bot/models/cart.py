from datetime import datetime

from sqlalchemy import INTEGER, VARCHAR, TEXT, DATETIME, ForeignKey, Numeric, BOOLEAN, FLOAT, BIGINT
from sqlalchemy.orm import mapped_column, Mapped

from .base import Base


class Cart(Base):
    __tablename__ = 'app_cart'
    id = mapped_column(INTEGER, primary_key=True, autoincrement=True)
    telegram_user_id = mapped_column(BIGINT, ForeignKey('app_telegramuser.id'), unique=True)


class CartProduct(Base):
    __tablename__ = 'app_cartproduct'
    id = mapped_column(INTEGER, primary_key=True, autoincrement=True)
    cart_id = mapped_column(INTEGER, ForeignKey('app_cart.id'))
    product_id = mapped_column(INTEGER, ForeignKey('app_product.id'))
    quantity = mapped_column(INTEGER, default=1)
