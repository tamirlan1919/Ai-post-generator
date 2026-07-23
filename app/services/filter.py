import logging
from collections import Counter
from dataclasses import dataclass, field
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import NewsItem
from app.repository.keyword_repo import KeywordRepository
from app.repository.post_repo import PostRepository

logger = logging.getLogger(__name__)

MIN_TEXT_LENGTH = 100



@dataclass
class FilterBatch:
    accepted: list[NewsItem] = field(default_factory=list)
    rejected_ids: list[str] = field(default_factory=list)
    reasons: Counter[str] = field(default_factory=Counter)


class FilterService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def filter_news(self, items: list[NewsItem]) -> FilterBatch:
        result = FilterBatch()

        if not items:
            return result

        keywords = {

        }