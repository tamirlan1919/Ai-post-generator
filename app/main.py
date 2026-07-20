from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.sources import router as sources_router
from app.database import engine, Base
import logging
from contextlib import asynccontextmanager


logging.basicConfig(
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info('База данных инициализирована')
    yield
    await engine.dispose()
    logger.info('Соеденение с БД закрыты')



app = FastAPI(
      title='AI news Bot API',
      description='Управление источниками, ключевыми словами и историей постов',
      version='1.0.0',
      lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins = ['http://localhost:3000'],
    allow_credentials = True,
    allow_methods = ['*'],
    allow_headers = ['*']
)

app.include_router(sources_router)

@app.get('/health', tags=['System'])
async def health_check():
    return {'status': 'ok'}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run("app:app.main", reload=True)