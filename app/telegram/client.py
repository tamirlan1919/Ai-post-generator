import logging

from telethon import TelegramClient

from app.config import settings

logger = logging.getLogger(__name__)

telegram_client = TelegramClient(
    settings.tg_session_name,
    settings.tg_api_id,
    settings.tg_api_hash
)


async def get_telegram_client() -> TelegramClient:
    if not telegram_client.is_connected():
        logger.info('Подключаем Telethon клиент...')
        await telegram_client.start()
        me = await telegram_client.get_me()
        logger.info(f'Telethon подключён как @{me.username}')
    return telegram_client
