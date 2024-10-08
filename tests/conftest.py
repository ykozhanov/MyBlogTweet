import os
from typing import AsyncGenerator

import pytest
from dotenv import load_dotenv
from httpx import ASGITransport, AsyncClient
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

load_dotenv()
os.environ["ENV"] = "test"

if os.getenv("ENV") == "test":
    from app.server.main import app as _app
    from app.server.models.models import Base, User
    from app.server.routes.routes import get_session

    from .factories import UserFactory

    url_engine = os.getenv("SQLALCHEMY_PATH_TEST_ASYNC")
    if not url_engine:
        raise ValueError("URL для тестовой базы данных не установлен")

    # NullPool создает новое соединение каждый раз, когда оно требуется, и закрывает его, когда оно больше не нужно
    engine = create_async_engine(url_engine, poolclass=NullPool)
    async_session = async_sessionmaker(
        expire_on_commit=False,
        bind=engine,
    )

    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        """
        Переопределяет зависимость получения сессии для тестирования.

        Возвращает:
            AsyncGenerator[AsyncSession, None]: Асинхронный генератор сессии базы данных.
        """
        async with async_session() as s:
            yield s

    _app.dependency_overrides[get_session] = override_get_session

    @pytest.fixture(scope="session", autouse=True)
    async def setup_test_db() -> AsyncGenerator[None, None]:
        """
        Настраивает тестовую базу данных перед запуском тестов.

        Создает новую базу данных, сбрасывает существующие таблицы и заполняет их тестовыми данными 10 пользователей.
        После завершения тестов удаляет базу данных.
        """
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

        async with async_session() as s:
            UserFactory._meta.sqlalchemy_session_factory = lambda: s  # type: ignore[misc, attr-defined]
            new_user: list[User] = UserFactory.create_batch(10)
            s.add_all(new_user)
            await s.commit()

        yield

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()

    @pytest.fixture
    async def session() -> AsyncGenerator[AsyncSession, None]:
        """
        Создает новую асинхронную сессию для тестов.

        Возвращает:
            AsyncGenerator[AsyncSession, None]: Асинхронный генератор сессии базы данных.
        """
        async with async_session() as s:
            yield s

    @pytest.fixture
    async def client() -> AsyncGenerator[AsyncClient, None]:
        """
        Создает асинхронного клиента для тестирования HTTP-запросов.

        Возвращает:
            AsyncGenerator[AsyncClient, None]: Асинхронный клиент для выполнения запросов к приложению.
        """
        async with AsyncClient(transport=ASGITransport(app=_app)) as c:
            yield c
