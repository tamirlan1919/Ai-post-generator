from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Source
from app.schemas import SourceCreate, SourceUpdate
from typing import Optional


class SourceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: SourceCreate) -> Source:
        """Создаёт новый источник. Возвращает объект с заполненным id."""
        source = Source(
            name=data.name,
            source_type=data.source_type,
            url=data.url,
            enabled=data.enabled,
        )
        self.session.add(source)
        await self.session.commit()
        # refresh — перечитывает объект из БД.
        # Нужен чтобы получить id, created_at которые проставила БД.
        await self.session.refresh(source)
        return source

    async def get_by_id(self, source_id: int) -> Optional[Source]:
        """Возвращает источник или None. Роутер решает что делать с None."""
        result = await self.session.execute(
            select(Source).where(Source.id == source_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self, enabled_only: bool = False) -> list[Source]:
        """Список всех источников. enabled_only=True — только активные."""
        stmt = select(Source).order_by(Source.created_at.desc())
        if enabled_only:
            stmt = stmt.where(Source.enabled == True)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update(self, source_id: int, data: SourceUpdate) -> Optional[Source]:
        """Обновляет только переданные поля (PATCH-семантика)."""
        # exclude_unset=True — только поля которые явно передал клиент.
        # Клиент передал только enabled=False? Обновляем только его.
        values = data.model_dump(exclude_unset=True)
        if not values:
            return await self.get_by_id(source_id)

        await self.session.execute(
            update(Source).where(Source.id == source_id).values(**values)
        )
        await self.session.commit()
        return await self.get_by_id(source_id)

    async def delete(self, source_id: int) -> bool:
        """Удаляет источник. Возвращает True если нашли и удалили."""
        source = await self.get_by_id(source_id)
        if source is None:
            return False
        await self.session.delete(source)
        await self.session.commit()
        return True

    async def exists_by_url(self, url: str) -> bool:
        """Проверяем дубликат перед добавлением нового источника."""
        result = await self.session.execute(
            select(Source.id).where(Source.url == url)
        )
        return result.scalar_one_or_none() is not None
