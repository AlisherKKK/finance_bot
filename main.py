import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio

from database import Database
from handlers import register_handlers
from config import BOT_TOKEN

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Инициализация базы данных
db = Database()


async def main():
    """Главная функция запуска бота"""
    try:
        # Создание таблиц в БД
        await db.create_tables()

        # Регистрация обработчиков
        register_handlers(dp, db)

        # Удаление вебхуков и запуск поллинга
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Бот запущен и готов к работе!")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())
