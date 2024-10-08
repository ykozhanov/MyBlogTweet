from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.server.models.models import User


async def test_follow(session: AsyncSession, client: AsyncClient) -> None:
    async with session:
        get_user_select = await session.execute(select(User).where(User.id == 1))
    get_user: User | None = get_user_select.scalar_one_or_none()

    if not get_user:
        raise AssertionError("Пользователь не найден")

    api_key: str | None = get_user.api_key
    if not api_key:
        raise AssertionError("api_key не найден")

    response = await client.post(
        "http://testhost/api/users/2/follow", headers={"api-key": api_key}
    )
    assert response.status_code == 201
    assert response.json()["result"] is True


async def test_repeat_follow(session: AsyncSession, client: AsyncClient) -> None:
    async with session:
        get_user_select = await session.execute(select(User).where(User.id == 1))
    get_user: User | None = get_user_select.scalar_one_or_none()

    if not get_user:
        raise AssertionError("Пользователь не найден")

    api_key: str | None = get_user.api_key
    if not api_key:
        raise AssertionError("api_key не найден")

    response = await client.post(
        "http://testhost/api/users/2/follow", headers={"api-key": api_key}
    )

    assert response.status_code == 409
    assert response.json()["result"] is False


async def test_unfollow(session: AsyncSession, client: AsyncClient) -> None:
    async with session:
        get_user_select = await session.execute(select(User).where(User.id == 1))
    get_user: User | None = get_user_select.scalar_one_or_none()

    if not get_user:
        raise AssertionError("Пользователь не найден")

    api_key: str | None = get_user.api_key
    if not api_key:
        raise AssertionError("api_key не найден")

    response = await client.delete(
        "http://testhost/api/users/2/follow", headers={"api-key": api_key}
    )

    assert response.status_code == 200
    assert response.json()["result"] is True


async def test_repeat_unfollow(session: AsyncSession, client: AsyncClient) -> None:
    async with session:
        get_user_select = await session.execute(select(User).where(User.id == 1))
    get_user: User | None = get_user_select.scalar_one_or_none()

    if not get_user:
        raise AssertionError("Пользователь не найден")

    api_key: str | None = get_user.api_key
    if not api_key:
        raise AssertionError("api_key не найден")

    response = await client.delete(
        "http://testhost/api/users/2/follow", headers={"api-key": api_key}
    )

    assert response.status_code == 404
    assert response.json()["result"] is False


async def test_get_user_me(session: AsyncSession, client: AsyncClient) -> None:
    async with session:
        get_user_select = await session.execute(select(User).where(User.id == 1))
    get_user: User | None = get_user_select.scalar_one_or_none()

    if not get_user:
        raise AssertionError("Пользователь не найден")

    api_key: str | None = get_user.api_key
    if not api_key:
        raise AssertionError("api_key не найден")

    response = await client.get(
        "http://testhost/api/users/me", headers={"api-key": api_key}
    )

    assert response.status_code == 200
    assert response.json()["result"] is True
    assert response.json()["user"]["id"] == get_user.id
    assert isinstance(response.json()["user"]["followers"], list)
    assert not response.json()["user"]["followers"]
    assert isinstance(response.json()["user"]["following"], list)
    assert not response.json()["user"]["following"]
