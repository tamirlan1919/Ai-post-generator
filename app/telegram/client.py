import os
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
        logger.info(f'Подключаем Телеграм клиент...')
        await telegram_client.start()
        me = await telegram_client.get_me()
        logger.info(f'Telthon connected for {me.username}')
    return telegram_client

