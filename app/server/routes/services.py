import os
from typing import Optional

import aiofiles
from config import MAX_FILE_SIZE
from fastapi import UploadFile
from models.models import Follow, Like, Media, Tweet, User
from schemas.schemas import (
    AuthorSchema,
    LikeSchema,
    MediaOutSchema,
    SuccessOutSchema,
    SuccessOutUserSchema,
    TweetInSchema,
    TweetOutForListSchema,
    TweetOutSchema,
    TweetsOutSchema,
    UserOutSchema,
    UserSchema,
)
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .utils import create_path_img, sorted_tweets


class TweetService:
    """
    Сервис для работы с твитами.

    Атрибуты:
        _session (AsyncSession): Асинхронная сессия базы данных.
        _api_key (str): API ключ пользователя.
    """

    def __init__(self, session: AsyncSession, api_key: str):
        self._session = session
        self._api_key = api_key

    async def _user(self) -> User | None:
        """
        Получает пользователя по API ключу.

        Возвращает:
            User | None: Объект пользователя, если найден, иначе None.
        """
        user_select = await self._session.execute(
            select(User).where(User.api_key == self._api_key)
        )
        return user_select.scalar_one_or_none()

    async def get(self) -> TweetOutForListSchema | int:
        """
        Получает список твитов пользователя и его подписок.

        Возвращает:
            TweetOutForListSchema | int: Список твитов или код ошибки.
        """
        user = await self._user()

        if not user:
            return 401

        following_users_select = await self._session.execute(
            select(Follow.followed_id).where(Follow.follower_id == user.id)
        )
        following_users: list[int] = list(following_users_select.scalars().all())
        following_users.insert(0, int(user.id))

        tweets_list_select = await self._session.execute(
            select(Tweet).options(
                selectinload(Tweet.user),
                selectinload(Tweet.likes),
            )
        )
        # selectinload подгружает данные связанных атрибутов

        tweets_list: list[Tweet] = list(tweets_list_select.scalars().all())

        if not tweets_list:
            return TweetsOutSchema(tweets=[])

        tweets_sorted: list[Tweet] = sorted_tweets(
            tweets_list=tweets_list, following_users=following_users
        )

        tweets_list_out = TweetsOutSchema(
            tweets=[
                TweetOutForListSchema(
                    id=int(tweet.id),
                    content=str(tweet.content),
                    attachments=list(tweet.attachments),
                    author=AuthorSchema(
                        id=int(tweet.user.id), name=str(tweet.user.name)
                    ),
                    likes=[
                        LikeSchema(user_id=int(like.user.id), name=str(like.user.name))
                        for like in tweet.likes
                    ],
                )
                for tweet in tweets_sorted
            ]
        )

        return tweets_list_out

    async def post(self, tweet_data: TweetInSchema) -> TweetsOutSchema | int:
        """
        Создает новый твит.

        Параметры:
            tweet_data (TweetInSchema): Данные о твите.

        Возвращает:
            TweetsOutSchema | int: Созданный твит или код ошибки.
        """
        user = await self._user()

        if not user:
            return 401

        tweet = tweet_data.model_dump()
        tweet["user_id"] = user.id

        medias_select = await self._session.execute(select(Media.id))
        medias = medias_select.scalars()

        if tweet["tweet_media_ids"] and not set(tweet["tweet_media_ids"]).issubset(
            set(medias)
        ):
            return 404

        tweet_media_ids = tweet["tweet_media_ids"]

        if tweet_media_ids:
            attachments_models = await self._session.execute(
                select(Media.path_file).where(Media.id.in_(tweet_media_ids))
            )
            attachments = attachments_models.scalars().all()
            tweet["tweet_media_ids"] = attachments

        tweet["attachments"] = tweet.pop("tweet_media_ids")

        tweet_model = Tweet(**tweet)

        self._session.add(tweet_model)
        await self._session.commit()
        await self._session.refresh(tweet_model)
        return TweetOutSchema.model_validate(tweet_model)

    async def delete(self, tweet_id: int) -> SuccessOutSchema | int:
        """
        Удаляет твит по идентификатору.

        Параметры:
            tweet_id (int): Идентификатор твита.

        Возвращает:
            SuccessOutSchema | int: Результат удаления или код ошибки.
        """
        user = await self._user()

        if not user:
            return 401

        tweet = await self._session.get(Tweet, tweet_id)

        if not tweet:
            return 404

        if tweet.user.api_key != self._api_key:
            return 403

        await self._session.delete(tweet)
        await self._session.commit()

        return SuccessOutSchema(result=True)


class LikeService:
    """
    Сервис для работы с лайками на твитах.

    Атрибуты:
        _session (AsyncSession): Асинхронная сессия базы данных.
        _api_key (str): API ключ пользователя.
    """

    def __init__(self, session: AsyncSession, api_key: str):
        self._session = session
        self._api_key = api_key

    async def _user(self) -> User | None:
        """
        Получает пользователя по API ключу.

        Возвращает:
            User | None: Объект пользователя, если найден, иначе None.
        """
        user_select = await self._session.execute(
            select(User).where(User.api_key == self._api_key)
        )
        return user_select.scalar_one_or_none()

    async def post(self, tweet_id: int) -> SuccessOutSchema | int:
        """
        Ставит лайк на твит.

        Параметры:
            tweet_id (int): Идентификатор твита, на который ставится лайк.

        Возвращает:
            SuccessOutSchema | int: Результат операции или код ошибки.
        """
        user = await self._user()

        if not user:
            return 401

        tweet = await self._session.get(Tweet, tweet_id)

        if not tweet:
            return 404

        like = Like(tweet_id=tweet_id, user_id=user.id)

        self._session.add(like)

        try:
            await self._session.commit()
        except IntegrityError:
            await self._session.rollback()
            return 400

        return SuccessOutSchema(result=True)

    async def delete(self, tweet_id: int) -> SuccessOutSchema | int:
        """
        Убирает лайк с твита.

        Параметры:
            tweet_id (int): Идентификатор твита, с которого убирается лайк.

        Возвращает:
            SuccessOutSchema | int: Результат операции или код ошибки.
        """
        user = await self._user()

        if not user:
            return 401

        tweet_like_select = await self._session.execute(
            select(Like).where(
                Like.tweet_id == tweet_id,
                Like.user_id == user.id,
            )
        )

        tweet_like = tweet_like_select.scalar_one_or_none()

        if not tweet_like:
            return 404

        await self._session.delete(tweet_like)
        await self._session.commit()

        return SuccessOutSchema(result=True)


class MediaService:
    """
    Сервис для работы с медиафайлами.

    Атрибуты:
        _session (AsyncSession): Асинхронная сессия базы данных.
        _api_key (str): API ключ пользователя.
    """

    def __init__(self, session: AsyncSession, api_key: str):
        self._session = session
        self._api_key = api_key

    async def _user(self) -> User | None:
        """
        Получает пользователя по API ключу.

        Возвращает:
            User | None: Объект пользователя, если найден, иначе None.
        """
        user_select = await self._session.execute(
            select(User).where(User.api_key == self._api_key)
        )
        return user_select.scalar_one_or_none()

    async def post(self, file: UploadFile) -> MediaOutSchema | int:
        """
        Загружает новый медиафайл.

        Параметры:
            file (UploadFile): Загружаемый файл.

        Возвращает:
            MediaOutSchema | int: Данные о загруженном медиафайле или код ошибки.
        """
        user = await self._user()

        if not user:
            return 401

        content = await file.read()

        if file.filename is None:
            return 404

        filename, extension = os.path.splitext(file.filename)

        if len(content) > MAX_FILE_SIZE:
            return 400

        path_img = await create_path_img(user, filename, extension)

        async with aiofiles.open(path_img, "wb") as img:
            await img.write(content)

        media = Media(path_file=path_img, user_id=user.id)

        self._session.add(media)
        await self._session.commit()
        await self._session.refresh(media)

        return MediaOutSchema.model_validate(media)


class UserService:
    """
    Сервис для работы с пользователями.

    Атрибуты:
        _session (AsyncSession): Асинхронная сессия базы данных.
        _api_key (Optional[str]): API ключ пользователя (может быть None).
    """

    def __init__(self, session: AsyncSession, api_key: Optional[str] = None):
        self._session = session
        self._api_key = api_key

    async def _user(self, user_id: Optional[int] = None) -> User | None:
        """
        Получает пользователя по идентификатору или API ключу.

        Параметры:
            user_id (Optional[int]): Идентификатор пользователя (если указан).

        Возвращает:
            User | None: Объект пользователя, если найден, иначе None.
        """
        user_select = await self._session.execute(
            select(User)
            .options(
                selectinload(User.following).selectinload(Follow.followed),
                selectinload(User.followers).selectinload(Follow.follower),
            )
            .where(User.id == user_id if user_id else User.api_key == self._api_key)
        )
        return user_select.scalar()

    async def get(self, user_id: Optional[int] = None) -> SuccessOutUserSchema | int:
        """
        Получает данные о пользователе по идентификатору или API ключу.

        Параметры:
            user_id (Optional[int]): Идентификатор пользователя (если указан).

        Возвращает:
            SuccessOutUserSchema | int: Данные о пользователе или код ошибки.
        """
        user = await self._user(user_id=user_id)

        if not user:
            return 401

        user_data = UserOutSchema(
            id=int(user.id),
            name=str(user.name),
            followers=[
                UserSchema(id=int(follow.follower.id), name=str(follow.follower.name))
                for follow in user.followers
            ],
            following=[
                UserSchema(id=int(follow.followed.id), name=str(follow.followed.name))
                for follow in user.following
            ],
        )

        return SuccessOutUserSchema(user=user_data)


class FollowService:
    """
    Сервис для работы с подписками пользователей.

    Атрибуты:
         _session (AsyncSession): Асинхронная сессия базы данных.
         _api_key (str): API ключ пользователя.
    """

    def __init__(self, session: AsyncSession, api_key: str):
        self._session = session
        self._api_key = api_key

    async def _user(self) -> User | None:
        """
        Получает пользователя по API ключу.

        Возвращает:
            User | None: Объект пользователя, если найден, иначе None.
        """
        user_select = await self._session.execute(
            select(User).where(User.api_key == self._api_key)
        )
        return user_select.scalar_one_or_none()

    async def post(self, user_id: int) -> SuccessOutSchema | int:
        """
        Подписывается на другого пользователя.

        Параметры:
            user_id (int): Идентификатор пользователя для подписки.

        Возвращает:
            SuccessOutSchema | int: Результат операции или код ошибки.
        """
        user = await self._user()

        if not user:
            return 401

        if user.id == user_id:
            return 400

        following_user_select = await self._session.execute(
            select(User.id).where(User.id == user_id)
        )
        following_user = following_user_select.scalar_one_or_none()

        if not following_user:
            return 404

        following = Follow(follower_id=user.id, followed_id=user_id)

        self._session.add(following)

        try:
            await self._session.commit()
        except IntegrityError:
            await self._session.rollback()
            return 409

        return SuccessOutSchema(result=True)

    async def delete(self, user_id: int) -> SuccessOutSchema | int:
        """
        Отписывается от другого пользователя.

        Параметры:
            user_id (int): Идентификатор пользователя для отписки.

        Возвращает:
            SuccessOutSchema | int: Результат операции или код ошибки.
        """
        user = await self._user()

        if not user:
            return 401

        if user.id == user_id:
            return 400

        following_model = await self._session.execute(
            select(Follow).where(
                Follow.follower_id == user.id,
                Follow.followed_id == user_id,
            )
        )

        following = following_model.scalar_one_or_none()

        if not following:
            return 404

        await self._session.delete(following)
        await self._session.commit()

        return SuccessOutSchema(result=True)
