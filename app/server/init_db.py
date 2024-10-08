import asyncio

from database.database import async_session, engine
from models.models import Base, User
from sqlalchemy import select


async def init_db() -> None:
    """
    Инициализирует базу данных, создавая все таблицы.

    Эта функция выполняет команду создания всех таблиц, определенных в модели базы данных.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def add_test_user() -> None:
    """
    Добавляет тестовых пользователей в базу данных.
    """
    async with async_session() as session:
        existing_users = await session.execute(select(User.name))
        existing_users_names = {user for user in existing_users.scalars().all()}

        new_test_user = User(name="test_user", api_key="test")
        new_222_user = User(name="222_user", api_key="222")
        new_333_user = User(name="333_user", api_key="333")

        new_users = [new_test_user, new_222_user, new_333_user]
        new_users_for_add = []
        for user in new_users:
            if user.name not in existing_users_names:
                new_users_for_add.append(user)

        session.add_all(new_users_for_add)
        await session.commit()


async def main() -> None:
    """
    Основная функция для инициализации базы данных.
    """
    await init_db()
    await add_test_user()


if __name__ == "__main__":
    asyncio.run(main())
