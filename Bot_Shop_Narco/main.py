import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from app.handlers import router
from app.admin_handlers import router_admin
from app.database.models import async_main
from config import token

from middlewares.admin_check import IsAdmin

# Здесь главная функция мэйн, в ней включается логинг, обозначаются бот, диспетчер
# подключаются роутеры и запускается бот
# Также здесь запускается функция async_main, которая создаёт все базы данных
async def main():
    await async_main()
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token = token,
              default=DefaultBotProperties(
                  parse_mode='html'
              ))
    dp = Dispatcher()
    dp.include_routers(router, router_admin)
    await dp.start_polling(bot)

# Тут мы именно запускаем функцию мэйн с помощью run(main()) 
# и с помощью except ловим ошибки
if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error('Bot stopped')