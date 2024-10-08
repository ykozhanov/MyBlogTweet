import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.server.models.models import User


# Не нужно писать, так как настроил в pytest.ini
# @pytest.mark.asyncio
@pytest.mark.parametrize("user_id", [1, 2, 5, 9, 10])
async def test_add_tweet(
    session: AsyncSession, client: AsyncClient, user_id: int
) -> None:
    async with session:
        get_user_select = await session.execute(select(User).where(User.id == user_id))
    get_user: User | None = get_user_select.scalar_one_or_none()

    if not get_user:
        raise AssertionError("Пользователь не найден")

    api_key: str | None = get_user.api_key
    if not api_key:
        raise AssertionError("api_key не найден")

    new_tweet = {
        "tweet_data": "test tweet {num}".format(num=user_id),
    }
    response = await client.post(
        "http://testhost/api/tweets",
        headers={"api-key": api_key},
        json=new_tweet,
    )

    assert response.status_code == 201
    assert response.json()["result"] is True


async def test_like(session: AsyncSession, client: AsyncClient) -> None:
    async with session:
        get_user_select = await session.execute(select(User).where(User.id == 1))
    get_user: User | None = get_user_select.scalar_one_or_none()

    if not get_user:
        raise AssertionError("Пользователь не найден")

    api_key: str | None = get_user.api_key
    if not api_key:
        raise AssertionError("api_key не найден")

    response = await client.post(
        "http://testhost/api/tweets/1/likes", headers={"api-key": api_key}
    )

    assert response.status_code == 201
    assert response.json()["result"] is True


async def test_repeat_like(session: AsyncSession, client: AsyncClient) -> None:
    async with session:
        get_user_select = await session.execute(select(User).where(User.id == 1))
    get_user: User | None = get_user_select.scalar_one_or_none()

    if not get_user:
        raise AssertionError("Пользователь не найден")

    api_key: str | None = get_user.api_key
    if not api_key:
        raise AssertionError("api_key не найден")

    response = await client.post(
        "http://testhost/api/tweets/1/likes", headers={"api-key": api_key}
    )

    assert response.status_code == 400
    assert response.json()["result"] is False


async def test_dislike(session: AsyncSession, client: AsyncClient) -> None:
    async with session:
        get_user_select = await session.execute(select(User).where(User.id == 1))
    get_user: User | None = get_user_select.scalar_one_or_none()

    if not get_user:
        raise AssertionError("Пользователь не найден")

    api_key: str | None = get_user.api_key
    if not api_key:
        raise AssertionError("api_key не найден")

    response = await client.delete(
        "http://testhost/api/tweets/1/likes", headers={"api-key": api_key}
    )

    assert response.status_code == 200
    assert response.json()["result"] is True


async def test_repeat_dislike(session: AsyncSession, client: AsyncClient) -> None:
    async with session:
        get_user_select = await session.execute(select(User).where(User.id == 1))
    get_user: User | None = get_user_select.scalar_one_or_none()

    if not get_user:
        raise AssertionError("Пользователь не найден")

    api_key: str | None = get_user.api_key
    if not api_key:
        raise AssertionError("api_key не найден")

    response = await client.delete(
        "http://testhost/api/tweets/1/likes", headers={"api-key": api_key}
    )

    assert response.status_code == 404
    assert response.json()["result"] is False
