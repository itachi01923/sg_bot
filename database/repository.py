from sqlalchemy import select, insert

from database.database import Base, async_session_factory
from database.models import User, Crypto
from database.schemas import CryptoBase, UserBase, CryptoResponse


class BaseRepository:
    model: Base

    @classmethod
    async def find_all(cls, **filter_by):
        async with async_session_factory() as session:
            smtp = select(cls.model.__table__.columns).filter_by(**filter_by)
            result = await session.execute(smtp)

            return result.mappings().all()

    @classmethod
    async def find_one_or_none(cls, **filter_by):
        async with async_session_factory() as session:
            smtp = select(cls.model.__table__.columns).filter_by(**filter_by)
            result = await session.execute(smtp)

            return result.mappings().one_or_none()

    @classmethod
    async def insert_data(cls, **model_data):
        async with async_session_factory() as session:
            smtp = insert(cls.model).values(**model_data).returning(cls.model.__table__.columns)
            result = await session.execute(smtp)
            await session.commit()

            return result.mappings().one()

    @classmethod
    async def delete_data(cls, **filter_by):
        async with async_session_factory() as session:
            smtp = select(cls.model).filter_by(**filter_by)
            result = await session.execute(smtp)

            item = result.scalar_one_or_none()

            if not item:
                return False

            await session.delete(item)
            await session.commit()

            return True


class UserRepository(BaseRepository):
    model = User

    @classmethod
    async def insert_data(cls, **model_data):
        try:
            async with async_session_factory() as session:
                smtp = insert(cls.model).values(**model_data).returning(cls.model.__table__.columns)
                result = await session.execute(smtp)

                await session.commit()
                return result.mappings().one()
        except Exception as e:
            return False


class CryptoRepository(BaseRepository):
    model: Crypto = Crypto

    @classmethod
    async def insert_data(cls, model_data: CryptoBase):
        async with async_session_factory() as session:
            new_crypto: cls.model = Crypto(**model_data.model_dump())

            session.add(new_crypto)

            await session.commit()
            await session.refresh(new_crypto)

            return new_crypto

    @classmethod
    async def update_data(cls, symbol: str, percent: int):
        crypto: CryptoBase = await CryptoRepository.find_one_or_none(symbol=symbol)

        async with async_session_factory() as session:
            get_crypto = await session.get(cls.model, crypto.id)
            get_crypto.percent = percent

            await session.commit()
            await session.refresh(get_crypto)
