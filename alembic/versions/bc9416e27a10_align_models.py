"""Align the existing database with the current SQLAlchemy models.

Revision ID: bc9416e27a10
Revises: 8913449f03ef
Create Date: 2026-07-23 16:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'bc9416e27a10'
down_revision: Union[str, Sequence[str], None] = '8913449f03ef'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Старые строки могли иметь пустой summary. Сначала заполняем их,
    # затем включаем ограничение NOT NULL без потери новостей.
    op.execute(sa.text('UPDATE news_items SET summary = title WHERE summary IS NULL'))
    op.alter_column(
        'news_items',
        'summary',
        existing_type=sa.Text(),
        nullable=False,
    )

    op.add_column('posts', sa.Column('error_message', sa.Text(), nullable=True))
    op.alter_column(
        'posts',
        'published_at',
        existing_type=sa.DateTime(),
        nullable=True,
    )
    op.create_unique_constraint('uq_post_news_id', 'posts', ['news_id'])


def downgrade() -> None:
    op.drop_constraint('uq_post_news_id', 'posts', type_='unique')
    op.execute(sa.text('UPDATE posts SET published_at = created_at WHERE published_at IS NULL'))
    op.alter_column(
        'posts',
        'published_at',
        existing_type=sa.DateTime(),
        nullable=False,
    )
    op.drop_column('posts', 'error_message')
    op.alter_column(
        'news_items',
        'summary',
        existing_type=sa.Text(),
        nullable=True,
    )
