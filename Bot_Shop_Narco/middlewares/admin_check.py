from aiogram.filters import BaseFilter
from aiogram.types import Message

# Здесь мы создали класс для проверки на админа, он наследуется от BaseFilter
# И реализует метод __call__, который будет проверять фильтр
class IsAdmin(BaseFilter):

    # Здесь мы инициализируем параметр admin_ids, который будет хранить в себе ID админов
    def __init__(self, admin_ids) -> None:
        self.admin_ids = admin_ids

    # Тут мы проверяем, что ID пользователя есть в списке админов (self.admin_ids)
    # Если его нет, то вернётся False и ничего не произойдёт, апдейт не будет пойман
    # Если пользователь есть в списке админов, то вернётся True и обработчик обработает его уже в admin_handlers.py
    async def __call__(self, message: Message) -> bool:
        
        # str() необходим, поскольку in требует, чтобы слева была строка и выдаёт ошибку
        return str(message.from_user.id) in self.admin_ids