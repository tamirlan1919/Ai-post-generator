from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.repository.source_repo import SourceRepository
from app.schemas import SourceCreate, SourceUpdate, SourceResponse, MessageResponse


router = APIRouter(prefix='/api/v1/sources', tags=['Sources'])


@router.post('/', response_model=SourceResponse,
             status_code=status.HTTP_201_CREATED,
             summary='Добавить источник новостей')
async def create_source(
        data: SourceCreate,
        session: AsyncSession = Depends(get_session)
):
    """
    Добаляет новый RSS источник новостей
    :param data:
    :param session:
    :return:
    """
    repo = SourceRepository(session)
    if await repo.exists_by_url(data.url):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'Источник с URL {data.url} уже существует'
        )
    source = await repo.create(data)
    return source


@router.get('/', response_model=list[SourceResponse],
            summary='Получить список источников')
async def get_list_sources(
        enabled_only: bool = Query(False, description='Показать только активные'),
        session: AsyncSession = Depends(get_session)
):
    """
    Получить список источников
    :param enabled_only:
    :param session:
    :return:
    """
    repo = SourceRepository(session)
    return await repo.get_all(enabled_only=enabled_only)


@router.get('/{source_id}', response_model=SourceResponse,
            summary='Получить источник по айди')
async def get_source(
        source_id: int,
        session: AsyncSession = Depends(get_session)
):
    """
    Получить источник по его id
    :param source_id:
    :param session:
    :return:
    """
    repo = SourceRepository(session)
    source = await repo.get_by_id(source_id=source_id)
    if source is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Источник с id={source_id} не найден'
        )
    return source


@router.patch('/{source_id}', response_model=SourceResponse,
              summary='Обновить источник')
async def update_source(
    source_id: int,
    data: SourceUpdate,
    session: AsyncSession = Depends(get_session)
):
    repo = SourceRepository(session)
    source = await repo.update(source_id=source_id, data=data)
    if source is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Источник с id={source_id} не найден'
        )
    return source


@router.delete('/{source_id}', response_model=MessageResponse,
               summary='Удалить источник')
async def delete_source(
    source_id: int,
    session: AsyncSession = Depends(get_session)
):
    repo = SourceRepository(session)
    deleted = await repo.delete(source_id=source_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Источник с id={source_id} не найден'
        )
    return MessageResponse(
        message=f'Источник {source_id} удален'
    )

