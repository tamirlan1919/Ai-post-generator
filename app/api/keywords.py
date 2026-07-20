from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.repository.keyword_repo import KeywordRepository
from app.schemas import KeywordCreate, KeywordResponse, MessageResponse
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix='/api/v1/keywords', tags=['Keywords'])


@router.post('/', response_model=KeywordResponse, status_code=201)
async def create_keyword(
        data: KeywordCreate,
        session: AsyncSession = Depends(get_session),
):
    repo = KeywordRepository(session)
    if await repo.exists(data.word):
        raise HTTPException(status_code=409, detail=f'Слово "{data.word}" уже есть')
    return await repo.create(data)


@router.get('/', response_model=list[KeywordResponse])
async def list_keywords(session: AsyncSession = Depends(get_session)):
    return await KeywordRepository(session).get_all()


@router.delete('/{keyword_id}', response_model=MessageResponse)
async def delete_keyword(
        keyword_id: int,
        session: AsyncSession = Depends(get_session),
):
    deleted = await KeywordRepository(session).delete(keyword_id)
    if not deleted:
        raise HTTPException(status_code=404, detail='Ключевое слово не найдено')
    return MessageResponse(message=f'Слово {keyword_id} удалено')
