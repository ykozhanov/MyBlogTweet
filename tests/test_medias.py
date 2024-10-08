import os
import shutil

import aiofiles
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.server.models.models import User


async def test_add_tweet_with_media_fall(
    session: AsyncSession, client: AsyncClient
) -> None:
    async with session:
        get_user_select = await session.execute(select(User).where(User.id == 1))
    get_user: User | None = get_user_select.scalar_one_or_none()

    if not get_user:
        raise AssertionError("Пользователь не найден")

    api_key: str | None = get_user.api_key
    if not api_key:
        raise AssertionError("api_key не найден")

    new_tweet = {"tweet_data": "test tweet with media", "tweet_media_ids": [1]}
    response = await client.post(
        "http://testhost/api/tweets",
        headers={"api-key": api_key},
        json=new_tweet,
    )

    assert response.status_code == 404
    assert response.json()["result"] is False


async def test_add_media(session: AsyncSession, client: AsyncClient) -> None:
    async with session:
        get_user_select = await session.execute(select(User).where(User.id == 1))
    get_user: User | None = get_user_select.scalar_one_or_none()

    if not get_user:
        raise AssertionError("Пользователь не найден")

    api_key: str | None = get_user.api_key
    if not api_key:
        raise AssertionError("api_key не найден")

    img_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "images", "winter-1.jpg"
    )

    async with aiofiles.open(img_path, "rb") as img_file:
        file = await img_file.read()
        response = await client.post(
            "http://testhost/api/medias",
            headers={"api-key": api_key},
            files={"file": ("winter-1.jpg", file, "image/jpeg")},
        )

    assert response.status_code == 201
    assert response.json()["media_id"] == 1
    assert response.json()["result"] is True


async def test_add_tweet_with_media(session: AsyncSession, client: AsyncClient) -> None:
    async with session:
        get_user_select = await session.execute(select(User).where(User.id == 1))
    get_user: User | None = get_user_select.scalar_one_or_none()

    if not get_user:
        raise AssertionError("Пользователь не найден")

    api_key: str | None = get_user.api_key
    if not api_key:
        raise AssertionError("api_key не найден")

    new_tweet = {"tweet_data": "test tweet with media", "tweet_media_ids": [1]}
    response = await client.post(
        "http://testhost/api/tweets",
        headers={"api-key": api_key},
        json=new_tweet,
    )

    assert response.status_code == 201
    assert response.json()["result"] is True


async def test_check_tweets(session: AsyncSession, client: AsyncClient) -> None:
    async with session:
        get_user_select = await session.execute(select(User).where(User.id == 1))
    get_user: User | None = get_user_select.scalar_one_or_none()

    if not get_user:
        raise AssertionError("Пользователь не найден")

    api_key: str | None = get_user.api_key
    if not api_key:
        raise AssertionError("api_key не найден")

    response = await client.get(
        "http://testhost/api/tweets", headers={"api-key": api_key}
    )

    assert response.status_code == 200
    assert response.json()["result"] is True
    assert response.json()["tweets"][0]["attachments"] == ["./images/1/winter-1.jpg"]


def test_check_exist_files() -> None:
    files_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images", "1")
    img_path = os.path.join(files_path, "winter-1.jpg")
    assert os.path.exists(img_path)
    shutil.rmtree(files_path)
