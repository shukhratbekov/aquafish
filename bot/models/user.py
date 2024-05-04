from datetime import datetime

from sqlalchemy import INTEGER, VARCHAR, TEXT, DATETIME, ForeignKey, BIGINT
from sqlalchemy.orm import mapped_column, Mapped

from .base import Base


class TelegramUser(Base):
    __tablename__ = 'app_telegramuser'
    id: Mapped[int] = mapped_column(INTEGER, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BIGINT, unique=True)
    first_name: Mapped[str] = mapped_column(VARCHAR(256))
    last_name: Mapped[str] = mapped_column(VARCHAR(256))
    username: Mapped[str] = mapped_column(VARCHAR(256), nullable=True)
    language: Mapped[str] = mapped_column(VARCHAR(10), default='ru')
    created_at: Mapped[datetime] = mapped_column(DATETIME, default=datetime.now())
