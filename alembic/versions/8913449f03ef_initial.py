"""Baseline schema created before Alembic was introduced.

Revision ID: 8913449f03ef
Revises:
Create Date: 2026-07-23 13:34:44.569567
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '8913449f03ef'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'sources',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('source_type', sa.String(length=20), nullable=False),
        sa.Column('url', sa.String(length=500), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint('url', name='sources_url_key'),
    )
    op.create_index('ix_sources_enabled', 'sources', ['enabled'])

    op.create_table(
        'keywords',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('word', sa.String(length=100), nullable=False),
        sa.Column('pattern', sa.String(length=200), nullable=True),
        sa.Column('enabled', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint('word', name='keywords_word_key'),
    )
    op.create_index('ix_keywords_enabled', 'keywords', ['enabled'])

    op.create_table(
        'news_items',
        sa.Column('id', sa.String(length=32), primary_key=True),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('url', sa.String(length=500), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('raw_text', sa.Text(), nullable=True),
        sa.Column('source_id', sa.Integer(), nullable=False),
        sa.Column('source_name', sa.String(length=200), nullable=False),
        sa.Column('published_at', sa.DateTime(), nullable=False),
        sa.Column('collected_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('is_processed', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['source_id'], ['sources.id'], name='news_items_source_id_fkey'),
    )
    op.create_index('ix_news_items_is_processed', 'news_items', ['is_processed'])
    op.create_index('ix_news_items_published_at', 'news_items', ['published_at'])
    op.create_index('ix_news_items_source_id', 'news_items', ['source_id'])
    op.create_index('ix_news_unprocessed_recent', 'news_items', ['is_processed', 'published_at'])

    op.create_table(
        'posts',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('news_id', sa.String(length=32), nullable=False),
        sa.Column('generated_text', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('published_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['news_id'], ['news_items.id'], name='posts_news_id_fkey'),
    )
    op.create_index('ix_posts_news_id', 'posts', ['news_id'])
    op.create_index('ix_posts_published_at', 'posts', ['published_at'])
    op.create_index('ix_posts_status', 'posts', ['status'])


def downgrade() -> None:
    op.drop_table('posts')
    op.drop_table('news_items')
    op.drop_table('keywords')
    op.drop_table('sources')
