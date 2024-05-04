from datetime import datetime

from sqlalchemy import INTEGER, VARCHAR, TEXT, DATETIME, ForeignKey, Numeric, BOOLEAN
from sqlalchemy.orm import mapped_column, Mapped

from .base import Base


class BaseProduct(Base):
    __tablename__ = 'app_product'
    id: Mapped[int] = mapped_column(INTEGER, primary_key=True, autoincrement=True)


class Product(Base):
    __tablename__ = 'app_product_translation'
    id: Mapped[int] = mapped_column(INTEGER, primary_key=True, autoincrement=True)
    language_code: Mapped[str] = mapped_column(VARCHAR(15))
    title: Mapped[str] = mapped_column(VARCHAR(256))
    description: Mapped[str] = mapped_column(TEXT, nullable=True)
    photo: Mapped[str] = mapped_column(VARCHAR(100), nullable=True)
    category_id: Mapped[int] = mapped_column(INTEGER, ForeignKey("app_category.id"))
    price: Mapped[float] = mapped_column(Numeric(precision=10, scale=2))
    is_active: Mapped[bool] = mapped_column(BOOLEAN, default=True)
    created_at: Mapped[datetime] = mapped_column(DATETIME, default=datetime.now())
    master_id: Mapped[int] = mapped_column(INTEGER, ForeignKey("app_product.id"))
