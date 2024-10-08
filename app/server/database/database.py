import os
from typing import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

load_dotenv()


def get_database_url() -> str:
    if os.environ.get("ENV") == "test":
        url_engine = os.getenv("SQLALCHEMY_PATH_TEST_ASYNC")
    else:
        url_engine = os.getenv("SQLALCHEMY_PATH_DEFAULT")

    if not url_engine:
        raise ValueError("URL для базы данных не установлен")

    return url_engine


engine = create_async_engine(get_database_url())
async_session = async_sessionmaker(
    autocommit=False, autoflush=False, bind=engine, expire_on_commit=False
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
