from sqlalchemy import String, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column

from database.database import Base


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Crypto(Base):
    __tablename__ = "crypto"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    symbol: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    is_active: Mapped[str] = mapped_column(Boolean, default=True, nullable=False)
    percent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
