from sqlalchemy import BigInteger, String, ForeignKey, Table, Column
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

# Создаём движок бд
engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3')

# Создаём сессию
async_session = async_sessionmaker(engine)

# Создаём класс Base, остальные по отношению к нему будут дочерними
# А он в свою очередь является дочерним для AsyncAttrs и DeclarativeBase
class Base(AsyncAttrs, DeclarativeBase):
    pass

# Таблица, где будут храниться данные о районах в которых есть товар
products_districts_association = Table(
    # Здесь указываем название таблицы
    'products_districts_association',
    # Тут мы сообщаем, что это таблица
    Base.metadata,
    # Тут мы создаём первый столбец, который хранит в себе айди продукта 
    # Column('product_id', Это имя колонки
    # ForeignKey('products.id') Здесь мы говорим, что это значение существует в таблице товаров в колонке id
    # primary_key=True) Тут мы делаем колонку частью ключа, чтобы комбинации product_id+district_id не повторялись
    Column('product_id',
           ForeignKey('products.id'),
           primary_key=True),
    Column('district_id',
           ForeignKey('districts.id'),
           primary_key=True)
)


# Здесь будет таблица сообщений, которые будет отправлять бот 
# Чтобы их было проще хранить и редактировать принял решение делать это через бд
class Message(Base):
    __tablename__ = 'messages'

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column()
    text: Mapped[str] = mapped_column()



# Это таблица городов в которых работает шоп
class City(Base):
    __tablename__ = 'cities'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)



# Это таблица районов, где есть товар
class District(Base):
    __tablename__ = 'districts'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    city_id: Mapped[int] = mapped_column(ForeignKey('cities.id'))
    # Это связь, что район может быть в одном городе
    city: Mapped['City'] = relationship()

    products = relationship('Product',
                            secondary=products_districts_association,
                            back_populates='districts')




# Это бд с продуктами, которые будут продаваться
class Product(Base):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(25))
    price: Mapped[int] = mapped_column()

    city_id: Mapped[int] = mapped_column(ForeignKey('cities.id'))
    district_id: Mapped[int] = mapped_column(ForeignKey('districts.id'))
    
    # Тут мы устанавливаем связь между городом и районом, чтобы если нужно
    # можно было их подгрузить отсюда
    city: Mapped['City'] = relationship()
    district: Mapped['District'] = relationship()

    districts = relationship('District',
                             secondary=products_districts_association,
                             back_populates='products')


# Таблица с методами оплаты
class Pay_Method(Base):
    __tablename__ = 'pay_methods'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()





# Создаём класс User, где будут храниться данные пользователя
# Пока что будут только баланс и айди, позжe добавлю больше переменных
class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    user_balance: Mapped[int] = mapped_column()



# Сюда надо будет ещё добавить бд для отзывов





# Функция, которая создаёт таблицы
async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)