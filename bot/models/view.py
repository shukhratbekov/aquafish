from datetime import datetime

from sqlalchemy import INTEGER, VARCHAR, TEXT, DATETIME, ForeignKey, Numeric, BOOLEAN
from sqlalchemy.orm import mapped_column, Mapped

from models.base import Base


class Review(Base):
    __tablename__ = 'app_review'
    id: Mapped[int] = mapped_column(INTEGER, primary_key=True, autoincrement=True)
    telegram_user_id: Mapped[int] = mapped_column(INTEGER, ForeignKey('app_telegramuser.id', ondelete='SET NULL'),
                                                  nullable=True)
    view : Mapped[str] = mapped_column(TEXT, nullable=False)
    created_at: Mapped[int] = mapped_column(DATETIME, default=datetime.now())