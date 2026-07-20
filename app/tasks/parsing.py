import asyncio
import logging
from celery_worker import celery_app
from app.config import settings
from app.database import  AsyncSessionLocal


logger = logging.getLogger(__name__)


def get_sync_session():
    return AsyncSessionLocal()


@celery_app.task(
    bind=True,
    name='tasks.parse_rss_source',
    max_retries=3,
    default_retry_delay=60,
    time_limit = 120
)
def parse_rss_source(self, source_id: int, source_name: str, url: str):
    async def _run() -> int:
        from app.news_parser.rss import RSSParser
        from app.repository.news_repo import NewsRepository

        parser = RSSParser(
            source_id=source_id,
            source_name=source_name,
            url=url,
            max_items=settings.max_news_per_source
        )
        items = parser.parse()

        if not items:
            return 0
        async with get_sync_session() as session:
            repo = NewsRepository(session)
            saved = await repo.save_batch(items)
            return saved

    try:
        return asyncio.run(_run())
    except Exception as e:
        raise self.retry(exc=e)



@celery_app.task(
    bind=True,
    name='tasks.parse_telegram_source',
    max_retries=2,
    default_retry_delay=60,
    time_limit = 120
)
def parse_telegram_source(self, source_id: int, source_name: str, channel: str):
    async def _run() -> int:
        from app.telegram.client import get_telegram_client
        from app.news_parser.telegram import TelegramChannelParser
        from app.repository.news_repo import NewsRepository

        clinet = await get_telegram_client()
        parser = TelegramChannelParser(
            clinet=clinet,
            source_id=source_id,
            source_name=source_name,
            channel_username=channel,
            max_items=settings.max_news_per_source
        )
        items = await parser.parse()

        if not items:
            return 0

        async with get_sync_session() as session:
            repo = NewsRepository(session)
            saved = await repo.save_batch(items)
            return saved

    try:
        return asyncio.run(_run())
    except Exception as e:
        raise self.retry(exc=e)


@celery_app.task(name='tasks.parse_all_sources')
def parse_all_sources():
    async def _get_sources():
        from app.database import AsyncSessionLocal
        from app.repository.source_repo import SourceRepository

        async with AsyncSessionLocal() as session:
            repo = SourceRepository(session)
            return await repo.get_all(enabled_only=True)

    sources = asyncio.run(_get_sources())
    logger.info(f'[pipeline] Запускаем парсинг для {len(sources)} источников')

    for source in sources:
        if source.source_type == 'rss':
            parse_rss_source.delay(
                source_id=source.id,
                source_name=source.name,
                url=source.url
            )
        elif source.source_type == 'telegram':
            parse_telegram_source.delay(
                source_id=source.id,
                source_name=source.name,
                channel=source.url
            )
    logger.info(f'[pipeline] Поставлено в очередь {len(sources)} задач')
    return len(sources)
