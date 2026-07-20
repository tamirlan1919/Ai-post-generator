from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Keyword
from app.schemas import KeywordCreate
from typing import Optional


class KeywordRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: KeywordCreate) -> Keyword:
        keyword = Keyword(
            word=data.word,  # уже lowercase из field_validator в схеме
            pattern=data.pattern,
            enabled=data.enabled,
        )
        self.session.add(keyword)
        await self.session.commit()
        await self.session.refresh(keyword)
        return keyword

    async def get_all_enabled(self) -> list[str]:
        """
        Возвращает список слов (не объектов) для быстрой проверки.
        Используется в FilterService: 'if any(kw in text for kw in keywords)'
        Проще работать с set[str] чем с list[Keyword].
        """
        result = await self.session.execute(
            select(Keyword.word).where(Keyword.enabled == True)
        )
        return list(result.scalars().all())

    async def get_all(self) -> list[Keyword]:
        result = await self.session.execute(
            select(Keyword).order_by(Keyword.word)
        )
        return list(result.scalars().all())

    async def delete(self, keyword_id: int) -> bool:
        kw = await self.session.get(Keyword, keyword_id)
        if kw is None:
            return False
        await self.session.delete(kw)
        await self.session.commit()
        return True

    async def exists(self, word: str) -> bool:
        result = await self.session.execute(
            select(Keyword.id).where(Keyword.word == word.lower())
        )
        return result.scalar_one_or_none() is not None
