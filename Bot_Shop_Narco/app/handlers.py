# Здесь импортируем из аиограм роутер и Ф фильтр
from aiogram import Router, F
import random, asyncio

# Здесь импортируем сообщения и колбэки из типов аиограм
from aiogram.types import Message, CallbackQuery
# Здесь импортируем команды из фильтров аиограм
from aiogram.filters import CommandStart, Command, StateFilter

from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

# Импортируем базу данных, как rq
import app.database.requests as rq


# Роутер
router = Router()

# Устанавливаем сепаратор, который будет определять, сколько будет тире у разделения
def separator(text: str):
    separator = '➖' * random.randint(1, 4)
    return text.replace('sep', separator)

class BuyProduct(StatesGroup):
    city = State()
    name = State()
    price = State()
    district = State()
    pay_method = State()
    confirm_pay = State()


# Команда старт добавляет пользователя в базу данных, если его там нет
# Также тут мы создаём приветственное сообщение, как у исходного бота 
# по-крайней мере пытаемся, вроде логика такая, мб и нет, но похоже выглядит
@router.message(CommandStart())
async def command_start(message: Message, state: FSMContext):
    # Здесь, если пользователя нет в бд, мы его добавляем
    await rq.set_and_get_user(message.from_user.id)

    # Здесь мы получаем данные юзера, а именно id and balance
    user = await rq.set_and_get_user(message.from_user.id)

    # Здесь мы получаем все города, которые хранятся в бд
    all_cities = await rq.get_all_cities()



    # Тут мы собираем сообщение, которое пользователь 
    # получит в итоге при использовании команды старт
    result = (f'{await rq.get_message_to_welcome("welcome")}\nsep\nПривет, <b>{user.tg_id}</b>\nВаш баланс: <b>💰{user.user_balance} руб</b>'
              f'\n{await rq.get_message_to_welcome('commands')}\nsep\n<b>Выберите город:</b>')
    
    # Тут мы добавляем в сообщение города, которые у нас есть в бд
    for one_city in all_cities:
        result += f'\nsep\n🏠 <b>{one_city.name}</b>\n[Для выбора нажмите 👉 /city{one_city.id}]'
    
    await message.answer(separator(result))
    await state.set_state(BuyProduct.city)


# Тут мы выводим город, в котором будем покупать что-то
@router.message(StateFilter(BuyProduct.city))
async def choose_city(message: Message, state: FSMContext):
    # Тут мы смотрим в каком состоянии находится пользователь
    current_state = await state.get_state()

    # Если пользователь уже выбрал город, то выбрать другой он не сможет 
    # благодаря этому if
    if current_state == BuyProduct.name:
        await message.answer(f'Выберите продукт строго из списка\nЧтобы вернуться в меню и начать сначала нажмите 👉 /start или @')
        return

    # Тут мы достаём из бд название города
    city_name = await rq.get_city(message.text.replace('/city', ''))
    
    # Если вернулось None, то мы отправим пользователю сообщение, 
    # что надо выбрать город из списка
    if city_name is None:
        await message.answer('Выберите город строго из списка!')
        return
    
    # Здесь мы обновляем состояние для города
    await state.update_data(city=city_name)

    # Здесь достаём продукты, которые есть в выбранном городе
    products = await rq.get_products(message.text.replace('/city', ''))

    # Здесь мы пишем ответ пользователю
    result = f'🏠 Город: <b>{city_name}</b>\nsep\nВыберите товар:\nsep\n'
    
    # Тут мы достаём из списка продуктов каждый список поочерёдно
    for product in products:
        result += (f'🎁 <b>{product.name}</b>\n💰 Цена: <b>{product.price} руб.</b>'
                   f'\n[ Для покупки нажмите 👉 /item{product.id} ]\n[ Посмотреть отзывы о данном товаре 👉 /reviews{product.id} ]\nsep\n')
    
    # Здесь добавляем в конец сообщения ендинг(окончание для сообщения) из базы данных
    result += await rq.get_message_to_welcome('end_for_products')
    
    await message.answer(separator(result))

    # Здесь мы устанавливаем состояние для выбора продукта
    await state.set_state(BuyProduct.name)



# Здесь мы выводим товар который есть в выбранном городе
@router.message(StateFilter(BuyProduct.name))
async def choose_item(message: Message, state: FSMContext):
    # Здесь мы подгружаем данные из бд, чтобы заполнить состояния и взять районы, 
    # в которых есть товар
    about_product = await rq.get_product(message.text.replace('/item', ''))
    
    # Если при поиске продукта пользователь выбрал отсутствующий продукт вернется None
    # И мы отправим ему просьбу выбрать продукт из списка
    if about_product is None:
        await message.answer(f'Выберите продукт строго из списка\nsЧтобы вернуться в меню и начать сначала нажмите 👉 /start или @')
        return

    # Здесь мы заполняем состояния
    await state.update_data(name = about_product.name)
    await state.update_data(price = about_product.price)

    # И берем уже заполненные значения из состояний
    data = await state.get_data()

    # Тут собираем финальное сообщение, которое получит юзер
    result = (f'🏠 Город: <b>{data['city']}</b>\n🎁 Товар: <b>{data['name']}</b>\n💰 Цена: <b>{data['price']} руб.</b>'
             f'\nsep\nВыберите район:\n')
    for district in about_product.districts:
        result += f'sep\n🏃 район <b>{district.name}</b>\n[ Для выбора нажмите 👉 /district{district.id} ]\n'
    
    await message.answer(separator(result))
    
    # Устанавливаем состояние для района
    await state.set_state(BuyProduct.district)



@router.message(StateFilter(BuyProduct.district))
async def choose_district(message: Message, state: FSMContext):
    # Получаем данные о районе
    district = await rq.get_district(message.text.replace('/district', ''))
    
    # Тут мы получаем методы оплаты из бд
    pay_methods = await rq.get_pay_methods()

    # Если пользователь выберет не тот район или попытается выбрать что-то другое, 
    # то мы попросим, чтобы он выбирал район строго из списка
    if district is None:
        await message.answer('Выберите район строго из списка\nЧтобы вернуться в меню и начать сначала нажмите 👉 /start или @')
        return

    # Обновляем состояние и добавляем район, который выбрал пользователь
    await state.update_data(district=district.name)

    # Здесь мы берём заполненные значения
    data = await state.get_data()

    # Здесь собираем сообщение для пользователя
    result = (f'🏠 Город: <b>{data['city']}</b>\n🏃 Район: <b>{data['district']}</b>'
              f'\n🎁 Товар: <b>{data['name']}</b>\n💰 Цена: <b>{data['price']} руб.</b>'
              f'\nsep\nВыберите метод оплаты:\nsep')
    
    # Тут мы вставляем доступные методы оплаты
    for pay_method in pay_methods:
        result += f'\n{pay_method.name}\n[Для выбора нажмите 👉 /method{pay_method.id} ]\nsep'
    
    await message.answer(separator(result))

    # Устанавливаем состояние для методов оплаты
    await state.set_state(BuyProduct.pay_method)



@router.message(StateFilter(BuyProduct.pay_method))
async def choose_pay_method(message: Message, state: FSMContext):
    # Получаем данные о методе оплаты по полученному ID
    pay_method = await rq.get_pay_method(message.text.replace('/method',''))
    
    # Если пользователь выбрал не корректный метод 
    # просим выбрать доступный метод из списка 
    if pay_method is None:
        await message.answer('Выберите метод оплаты строго из списка\nЧтобы вернуться в меню и начать сначала нажмите 👉 /start или @')
        return
    
    # Обновляем значение состояния для метода оплаты
    await state.update_data(pay_method=pay_method.name)

    # Достаём значения из состояний
    data = await state.get_data()

    # Здесь собираем сообщение для пользователя
    result = (f'🏠 Город: <b>{data['city']}</b>\n🏃 Район: <b>{data['district']}</b>'
              f'\n🎁 Товар: <b>{data['name']}</b>\n💰 Цена: <b>{data['price']} руб.</b>'
              f'\n💱 Метод оплаты: <b>{data['pay_method']}</b>')
    
    #Если метод оплаты биткоином, что отвечаем так:
    if pay_method.id == 1:
        # Считаем сумму к оплате
        value_for_pay = int(data['price'].replace(' ', '')) / 8304159

        # Нужно будет добавить в базу данных для крипты её значение, 
        # чтобы парсилось и само в бд добавлялось, а цена высчитывалась от её курса
        result += (f'\nsep\nДля приобретения выбранного товара, оплатите'
                   f'\nsep\n💸 <code>{value_for_pay:.8f}</code>: <b>BTC</b>'
                   f'\nsep\nна Bitcoin кошелек:\n<code>{pay_method.description}</code>'
                   f'\nsep\n#⃣ Заказ №<code>{random.randint(200000, 220000)}</code>, запомните его.'
                   f'\nsep\nКомментарий к платежу\n💬 {random.randint(80000000, 100000000)}'
                   f'\n{await rq.get_message_to_welcome('ending_for_bitcoin')}')

        # Отправляем сообщение без предпросмотра ссылок
        await message.answer(separator(result),
                             disable_web_page_preview=True)

        # Устанавливаем состояние для подтверждения платежа
        await state.set_state(BuyProduct.confirm_pay)

    # Если метод оплаты лайткоин
    elif pay_method.id == 7:
        # Считаем сумму к оплате
        value_for_pay = int(data['price'].replace(' ', '')) / 8067

        # Собираем финальный ответ
        result += (f'\nsep\nДля приобретения выбранного товара, оплатите\nsep'
                   f'\n💸 <code>{value_for_pay:.8f}</code>: <b>LTC</b>'
                   f'\nна Litecoin кошелек:\nsep\n<code>{pay_method.description}</code>'
                   f'\nsep\n#⃣ Заказ №<code>{random.randint(2000, 220000)}</code>, запомните его.'
                   f'\nsep\nКомментарий к платежу\n💬 {random.randint(10000, 100000000)}'
                   f'\n{await rq.get_message_to_welcome('ending_for_litecoin')}')

        # Отправляем сообщение без предпросмотра ссылок
        await message.answer(separator(result),
                             disable_web_page_preview=True)
        
        # Устанавливаем состояние для подтверждения платежа
        await state.set_state(BuyProduct.confirm_pay)


@router.message(StateFilter(BuyProduct.confirm_pay))
async def confirm_pay(message: Message, state: FSMContext):
    # Достаём уже заполненные значения
    data = await state.get_data()

    # Если пользователь выбирал биткоин для пополнения и подтвердил перевод, 
    # то его будет морозить сообщение о том, что у транзакции 0 подтверждений
    if data['pay_method'] == 'Bitcoin':
        # Бот на время засыпает, типа что-то проверяет
        await asyncio.sleep(random.randint(2, 5))

        # Отвечаем, что ничего нет
        await message.answer(separator(await rq.get_message_to_welcome('pay_refuse_bitcoin')))
        return
    elif data['pay_method'] == 'Litecoin':
        # Бот на время засыпает, типа что-то проверяет
        await asyncio.sleep(random.randint(2, 5))

        # Отвечаем, что ничего нет
        await message.answer(separator(await rq.get_message_to_welcome('pay_refuse_litecoin')))
        return
    



