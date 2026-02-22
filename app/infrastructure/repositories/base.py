from typing import Generic, TypeVar, Type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

T = TypeVar("T")


class BaseRepository(Generic[T]):
    def __init__(self, session: AsyncSession, model: Type[T]):
        self.session = session
        self.model = model

    async def get(self, id: int) -> T | None:
        return await self.session.get(self.model, id)

    async def list(self, limit: int = 100, offset: int = 0) -> list[T]:
        q = select(self.model).limit(limit).offset(offset)
        result = await self.session.execute(q)
        return result.scalars().all()

    async def create(self, obj_in: dict) -> T:
        db_obj = self.model(**obj_in)
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def update(self, db_obj: T, update_data: dict) -> T:
        for k, v in update_data.items():
            setattr(db_obj, k, v)
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def delete(self, id: int) -> T | None:
        obj = await self.get(id)
        if obj:
            await self.session.delete(obj)
            await self.session.commit()
        return obj
