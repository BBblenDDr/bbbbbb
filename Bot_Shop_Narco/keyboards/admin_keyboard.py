from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Главная клавиатура для добавления/удаления позиций/города
# Также можно добавить что-то типа выгрузки базы данных или логов
main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Добавить позицию',
                          callback_data='add_position'),
     InlineKeyboardButton(text='Удалить позицию',
                          callback_data='del_position')],
    [InlineKeyboardButton(text='Добавить город',
                          callback_data='add_city'),
     InlineKeyboardButton(text='Удалить город',
                          callback_data='del_city')]
])