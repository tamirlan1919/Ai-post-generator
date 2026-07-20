import feedparser
import logging
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from app.models import NewsItem


logger = logging.getLogger(__name__)

MAX_SUMMARY_LEN = 1000


def _clean_html(html_text: str) -> str:
    if not html_text:
        return ''
    return BeautifulSoup(html_text, 'lxml').get_text(separator=' ').strip()


def _parse_date(entry) -> datetime:
    pub_date = entry.get('pubDate')
    if pub_date:
        return datetime(**pub_date, tzinfo=timezone.utc)
    logger.warning(f'Нет даты публикации для {entry.get("title")}')
    return datetime.now(timezone.utc)


class RSSParser:
    def __init__(self, source_id: int, source_name: str, url: str, max_items: int = 10):
        self.source_id = source_id
        self.source_name = source_name
        self.url = url
        self.max_items = max_items

    def parse(self) -> list[dict]:
        logger.info(f'RSS Парсим: {self.url}')
        feed = feedparser.parse(self.url)
        status = getattr(feed, 'status', 200)
        if status not in (200, 301, 302):
            return []
        if feed.bozo:
            logger.warning()
        results = []
        for entry in feed.entries[:self.max_items]:
            title = entry.get('title').strip()
            link = entry.get('link', '')

            if not title:
                continue

            raw_summary = entry.get('summary') or entry.get('description')

            summary = _clean_html(raw_summary)[:MAX_SUMMARY_LEN]

            if not summary:
                summary = title

            published_at = _parse_date(entry)

            news_id = NewsItem.make_id(url=link, title=title, source=self.source_name)
            results.append(
                {
                    'id': news_id,
                    'title': title,
                    'url': link or None,
                    'summary': summary,
                    'raw_text': None,
                    'source_id': self.source_id,
                    'source_name': self.source_name,
                    'published_at': published_at,
                    'is_processed': False
                }
            )
            #log TODO
            return results
