from datetime import datetime

from sqlalchemy import INTEGER, VARCHAR, TEXT, DATETIME, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from .base import Base


class BaseCategory(Base):
    __tablename__ = 'app_category'
    id: Mapped[int] = mapped_column(INTEGER, primary_key=True, autoincrement=True)
    parent_id: Mapped[int] = mapped_column(INTEGER, ForeignKey("app_category.id"), nullable=True)

    category = relationship("Category", back_populates="base_category")


class Category(Base):
    __tablename__ = 'app_category_translation'
    id: Mapped[int] = mapped_column(INTEGER, primary_key=True, autoincrement=True)
    language_code: Mapped[str] = mapped_column(VARCHAR(15))
    title: Mapped[str] = mapped_column(VARCHAR(256))
    description: Mapped[str] = mapped_column(TEXT, nullable=True)
    photo: Mapped[str] = mapped_column(VARCHAR(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DATETIME, default=datetime.now())
    master_id: Mapped[int] = mapped_column(INTEGER, ForeignKey("app_category.id"))

    base_category = relationship("BaseCategory", back_populates="category")
