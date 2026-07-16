from datetime import datetime
from sqlalchemy import (String, Text, Boolean, DateTime,
                        Integer, Index, UniqueConstraint, func, ForeignKey)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from enum import Enum as PyEnum
import hashlib


class Source(Base):
    __tablename__ = 'sources'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    source_type: Mapped[str] = mapped_column(String(20), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    news_items: Mapped[list['NewsItem']] = relationship(
        back_populates='source'
    )


class Keyword(Base):
    __tablename__ = 'keywords'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    word: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    pattern: Mapped[str] = mapped_column(String(200), nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class NewsItem(Base):
    __tablename__ = 'news_items'

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=True)
    summary: Mapped[str] = mapped_column(Text, nullable=True)
    raw_text:  Mapped[str or None] = mapped_column(Text, nullable=True)
    source_id: Mapped[int] = mapped_column(
        ForeignKey('sources.id'),
       nullable=False,
       index=True)
    source_name: Mapped[str] = mapped_column(String(200), nullable=False)
    published_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    collected_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    is_processed: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    source: Mapped['Source'] = relationship(
        back_populates='news_items'
    )
    post: Mapped['Post'] = relationship(
        back_populates='news_item',
        uselist=False
    )

    __table_args__ = (
        Index('ix_news_unprocessed_recent', 'is_processed', 'published_at')
    )

    @staticmethod
    def make_id(url: str or None, title: str, source: str) -> str:
        content = url or f'{title}:{source}'
        return hashlib.md5(content.encode()).hexdigest()


class PostStatus(str, PyEnum):
    PENDING = 'pending'
    GENERATED = 'generated'
    PUBLISHED = 'published'
    FAILED = 'failed'
    SKIPPED = 'skipped'


class Post(Base):
    __tablename__ = 'posts'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    news_id: Mapped[str] = mapped_column(
        ForeignKey('news_items.id'),
        nullable=False,
        index=True)
    generated_text: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[PostStatus] = mapped_column(
        String(20),
        default=PostStatus.PENDING,
        nullable=False,
        index=True
    )
    published_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    news_item: Mapped['NewsItem'] = relationship(
        back_populates='post'
    )

    __talbe_args__ = (
        UniqueConstraint('news_id', name='uq_post_news_id'),
    )
