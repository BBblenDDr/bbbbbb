# Здесь импортируем из аиограм роутер и Ф фильтр
from aiogram import Router, F
# Здесь импортируем сообщения и колбэки из типов аиограм
from aiogram.types import Message, CallbackQuery
# Здесь импортируем команды из фильтров аиограм
from aiogram.filters import Command
# Импортируем базу данных, как rq
import app.database.requests as rq
# Импортируем айди админa
from config import admin_ids
# Импортируем клавиатуру админа
import keyboards.admin_keyboard as kb
# Здесь мы импортируем фильтр для проверки на админа 
# пока что он находится в мидлварях, надо будет его потом перенести
from middlewares.admin_check import IsAdmin
# Роутер
router_admin = Router()

# Команда для того, чтобы попасть в админское меню
@router_admin.message(IsAdmin(admin_ids), Command('admin'))
async def command_admin(message: Message):
    # Выводит клавиатуру для работы с базами данных
    await message.answer('<b>Вы находитесь в админском меню</b>\nВыберите пункт меню:',
                         reply_markup=kb.main)

# Тут мы будем добавлять что-либо в бд
@router_admin.callback_query(F.data.startswith('add_'))
async def add_position(callback: CallbackQuery):
    await callback.answer()
    await callback.answer()

# Здесь мы будем удалять что-либо из бд

