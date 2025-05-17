from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database.models import async_session
from app.database.models import Message, User, City, Product, District, Pay_Method


# Здесь мы получаем данные о пользователе
# и если его нет в бд, то записываем его с нулевым балансом
async def set_and_get_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id==tg_id))
        if not user:
            session.add(User(tg_id=tg_id,
                             user_balance=0))
            await session.commit()
        
        return user
    

# Здесь мы по ключу получаем сообщения, которые хранятся в базе данных
# Ещё можно добавить fallback, если вдруг не будет найден ключ по которому 
# ищем сообщение
async def get_message_to_welcome(key):
    async with async_session() as session:
        result = await session.scalar(select(Message).where(Message.key==key))
    # Это возвращает именно текст сообщения, которое нам нужно
    return result.text



# Тут мы получаем города, которые у нас есть в бд
async def get_all_cities():
    async with async_session() as session:
        result = await session.scalars(select(City))
    return result.all()

# Тут получаем название города по его айди
async def get_city(id):
    async with async_session() as session:
        result = await session.scalar(
            select(City)
            .where(City.id==id))
        
        # Здесь выполняем проверку, есть ли город в бд, если нет, то возвращаем None 
        if result is None:
            return None
    return result.name



# Тут мы получаем товары, которые есть в выбранном городе
async def get_products(city_id):
    async with async_session() as session:
        result = await session.scalars(
            select(Product)
            .where(Product.city_id==city_id))
    return result.all()

# Тут мы берем один продукт из бд, который выбрал пользователь
async def get_product(id):
    async with async_session() as session:
        result = await session.scalar(
            select(Product)
            # Эта строка помогает нам сразу подгрузить связанные объекты, а именно disctricts
            .options(selectinload(Product.districts))
            .where(Product.id==id))
        if result is None:
            return None
    return result

# Здесь мы достаём из бд район
async def get_district(id):
    async with async_session() as session:
        result = await session.scalar(
            select(District)
            .where(District.id==id))
        if result is None:
            return None
    return result


# Тут мы отправляем все методы оплаты, что есть в бд
async def get_pay_methods():
    async with async_session() as session:
        result = await session.scalars(select(Pay_Method))
    return result

# Достаём метод оплаты по полученному ID
async def get_pay_method(id):
    async with async_session() as session:
        result = await session.scalar(
            select(Pay_Method)
            .where(Pay_Method.id==id))
        if result is None:
            return None
    return result
