import logging
import asyncio
from datetime import datetime, timezone, timedelta
from telethon import TelegramClient
from telethon.errors import FloodWaitError, ChannelPrivateError

from app.models import NewsItem

logger = logging.getLogger(__name__)

MIN_TEXT_LENGTH = 100
MAX_SUMMARY_LENGTH = 1000


class TelegramChannelParser:
    def __init__(self,
                 client: TelegramClient,
                 source_id: int,
                 source_name: str,
                 channel_username: str,
                 max_items: int = 10,
                 hours_back: int = 24
                 ):
        self.client = client
        self.source_id = source_id
        self.source_name = source_name,
        self.channel = channel_username
        self.max_items = max_items
        self.hours_back = hours_back

    async def parse(self) -> list[dict]:
        logger.info(f'[TG] Parsim channel {self.channel}')
        since = datetime.now(timezone.utc) - timedelta(hours=self.hours_back)

        results = []

        try:
            async for message in self.client.iter_messages(
                entity=self.channel,
                limit=self.max_items,
                offset_date=datetime.now(timezone.utc)
            ):
                if message.date < since:
                    break
                if message.forward:
                    continue
                text = message.text or ''
                if len(text) < MIN_TEXT_LENGTH:
                    continue
                title = text[:100].replace('\n', ' ').strip()

                if len(text) > 100:
                    title += '...'

                summary = text[:MAX_SUMMARY_LENGTH]

                raw_text = text
                url = f'https://t.me/{self.channel}/{message.id}'
                news_id = NewsItem.make_id(url=url, title=title, source=self.source_name)

                results.append(
                    {
                        'id': news_id,
                        'title': title,
                        'url': url,
                        'summary': summary,
                        'raw_text': raw_text,
                        'source_id': self.source_id,
                        'source_name': self.source_name,
                        'published_at': message.date,
                        'is_processed': False
                    }
                )
        except FloodWaitError as e:
            logger.warning(f'[TG] FloodWait')
            await asyncio.sleep(e.secconds + 5)
        except ChannelPrivateError as e:
            logger.error(f'[TG] Канал недоступен {self.channel}: {e}')
