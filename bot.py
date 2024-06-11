import asyncio
# import logging
import yaml

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
import logging.config
from aiogram.fsm.storage.redis import RedisStorage, Redis

from config_data.config import Config, load_config
from config_data.logging_settings import logging_config
from handlers import other_handlers, users_handlers, authorized_user_handlers, admin_handlers


# with open('../config_data/logging_config.yaml', 'rt') as f:
#     logging_config = yaml.safe_load(f.read())
# Инициализируем логгер
logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)

# redis = Redis(host='localhost')
# Инициализируем хранилище (создаем экземпляр класса MemoryStorage)
# storage = RedisStorage(redis=redis)
storage = MemoryStorage()


# Функция конфигурирования и запуска бота
async def main():
    # Конфигурируем логирование
    # logging.basicConfig(
    #     level=logging.INFO,
    #     format='%(filename)s:%(lineno)d #%(levelname)-8s '
    #            '[%(asctime)s] - %(name)s - %(message)s')

    # Выводим в консоль информацию о начале запуска бота
    logger.info('Starting bot')

    # Загружаем конфиг в переменную config
    config: Config = load_config()

    # Инициализируем бот и диспетчер
    bot = Bot(token=config.tg_bot.token,
              default=DefaultBotProperties(parse_mode='HTML')
              )
    dp = Dispatcher(storage=storage)
    dp['admin_ids'] = config.tg_bot.admin_ids

    # Регистриуем роутеры в диспетчере
    dp.include_router(admin_handlers.router)
    dp.include_router(authorized_user_handlers.router)
    dp.include_router(users_handlers.router)
    dp.include_router(other_handlers.router)

    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


asyncio.run(main())
