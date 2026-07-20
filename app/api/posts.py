from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.database import get_session
from app.models import Post, PostStatus
from app.schemas import PostResponse
from typing import Optional

router = APIRouter(prefix='/api/v1/posts', tags=['Posts'])


@router.get('/', response_model=list[PostResponse])
async def list_posts(
        status: Optional[str] = Query(None, description='Фильтр по статусу: pending/generated/published/failed'),
        limit: int = Query(20, ge=1, le=100),
        offset: int = Query(0, ge=0),
        session: AsyncSession = Depends(get_session),
):
    """
    История постов с фильтрацией по статусу.
    Сортировка: свежие сверху (ORDER BY created_at DESC).
    """
    stmt = select(Post).order_by(desc(Post.created_at)).limit(limit).offset(offset)
    if status:
        stmt = stmt.where(Post.status == status)
    result = await session.execute(stmt)
    return list(result.scalars().all())


@router.get('/{post_id}', response_model=PostResponse)
async def get_post(
        post_id: int,
        session: AsyncSession = Depends(get_session),
):
    post = await session.get(Post, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail=f'Пост {post_id} не найден')
    return post
