import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

import logging.config
from fluentogram import TranslatorHub

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy import text

from config_data.config import Config, load_config, DBConfig, load_db_config, GuidesConfig, load_guides_config
from config_data.logging_settings import logging_config
from handlers import other_handlers, users_handlers, authorized_user_handlers, admin_handlers
from middlewares import LogMiddleware, TranslatorRunnerMiddleware, DatabaseMiddleware
from utils.i18n import create_translator_hub
from database import Base

# Инициализируем логгер
logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)

# redis = Redis(host='localhost')
# Инициализируем хранилище (создаем экземпляр класса MemoryStorage)
# storage = RedisStorage(redis=redis)
storage = MemoryStorage()


# Функция конфигурирования и запуска бота
async def main():

    # Выводим в консоль информацию о начале запуска бота
    logger.info('Starting bot')

    # Загружаем конфиг в переменную config
    config: Config = load_config()
    config_db: DBConfig = load_db_config()
    guides_config: GuidesConfig = load_guides_config("..")

    engine = create_async_engine(url=config_db.db.db_address, echo=True)
    session = async_sessionmaker(engine, expire_on_commit=False)

    # Проверка соединения с СУБД
    async with engine.begin() as conn:
        await conn.execute(text("SELECT 1"))

    # Создание таблиц
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # Инициализируем бот и диспетчер
    bot = Bot(token=config.tg_bot.token,
              default=DefaultBotProperties(parse_mode='HTML')
              )
    dp = Dispatcher(storage=storage)
    dp['admin_ids'] = config.tg_bot.admin_ids

    # Создаем объект типа TranslatorHub
    translator_hub: TranslatorHub = create_translator_hub()

    # Регистриуем роутеры в диспетчере
    dp.include_router(admin_handlers.router)
    dp.include_router(authorized_user_handlers.router)
    dp.include_router(users_handlers.router)
    dp.include_router(other_handlers.router)

    # Регистрируем мидлварь для логирования пропушенных update
    dp.update.middleware(LogMiddleware())
    # Регистрируем миддлварь для i18n
    dp.update.middleware(TranslatorRunnerMiddleware())
    dp.update.middleware(DatabaseMiddleware(session=session))

    dp.workflow_data.update(some_id=config.tg_bot.admin_ids, plans=guides_config.plans,
                            vdot_guides=guides_config.vdot_guid,
                            koef=guides_config.koef)

    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, _translator_hub=translator_hub)


asyncio.run(main())
