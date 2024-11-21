from sqlalchemy import select

from database.database import async_session_factory, Base


class BaseRepository:
    model: Base = None

    @classmethod
    async def find_all(cls, **filter_by):
        async with async_session_factory() as session:
            query = select(cls.model.__table__.columns).filter_by(**filter_by)
            result = await session.execute(query)

            return result.mappings().all()

    @classmethod
    async def find_one_or_none(cls, **filter_by):
        async with async_session_factory() as session:
            query = select(cls.model.__table__.columns).filter_by(**filter_by)
            result = await session.execute(query)

            return result.mappings().one_or_none()

    @classmethod
    async def find_by_id_or_none(cls, model_id: int):
        async with async_session_factory() as session:
            query = select(cls.model.__table__.columns).filter_by(id=model_id)
            result = await session.execute(query)

            return result.mappings().one_or_none()

    @classmethod
    async def insert_data(cls, **model_data):
        async with async_session_factory() as session:
            session.add(cls.model(**model_data))
            await session.commit()

    @classmethod
    async def delete_item(cls, item_id, **kwargs) -> bool:
        async with async_session_factory() as session:
            stmt = select(cls.model).where(cls.model.id == item_id).filter_by(**kwargs)
            result = await session.execute(stmt)
            item = result.scalar_one_or_none()

            if not item:
                return False

            await session.delete(item)
            await session.commit()

            return True
