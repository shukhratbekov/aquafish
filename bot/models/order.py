from datetime import datetime

from sqlalchemy import INTEGER, VARCHAR, TEXT, DATETIME, ForeignKey, Numeric, BOOLEAN, FLOAT
from sqlalchemy.orm import mapped_column, Mapped

from .base import Base


class Order(Base):
    __tablename__ = 'app_order'
    id: Mapped[int] = mapped_column(INTEGER, primary_key=True, autoincrement=True)
    final_price: Mapped[float] = mapped_column(Numeric(precision=10, scale=2), default=0)
    telegram_user_id: Mapped[int] = mapped_column(INTEGER, ForeignKey('app_telegramuser.id', ondelete='SET NULL'),
                                                  nullable=True)
    payment: Mapped[str] = mapped_column(VARCHAR(10), default='process')
    phone_number: Mapped[str] = mapped_column(VARCHAR(128))
    status: Mapped[str] = mapped_column(VARCHAR(10))
    shipping: Mapped[bool] = mapped_column(BOOLEAN, default=False)
    created_at: Mapped[datetime] = mapped_column(DATETIME, default=datetime.now())


class OrderProduct(Base):
    __tablename__ = 'app_orderproduct'
    id: Mapped[int] = mapped_column(INTEGER, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(INTEGER, ForeignKey('app_order.id', ondelete='CASCADE'))
    product_id: Mapped[int] = mapped_column(INTEGER, ForeignKey('app_product.id', ondelete='SET NULL'))
    quantity: Mapped[int] = mapped_column(INTEGER, default=1)
    price: Mapped[float] = mapped_column(Numeric(precision=10, scale=2))

class OrderShipping(Base):
    __tablename__ = 'app_ordershipping'
    id: Mapped[int] = mapped_column(INTEGER, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(INTEGER, ForeignKey('app_order.id', ondelete='CASCADE'))
    address: Mapped[str] = mapped_column(VARCHAR(256))
    longitude: Mapped[float] = mapped_column(FLOAT)
    latitude: Mapped[float] = mapped_column(FLOAT)

