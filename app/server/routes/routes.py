from config import MAX_FILE_SIZE_MB
from database.database import get_session
from fastapi import APIRouter, Depends, Header, UploadFile
from fastapi.responses import JSONResponse
from schemas.schemas import (
    ExceptionOutSchema,
    MediaOutSchema,
    SuccessOutSchema,
    SuccessOutUserSchema,
    TweetInSchema,
    TweetOutSchema,
    TweetsOutSchema,
)
from sqlalchemy.ext.asyncio import AsyncSession

from .services import (
    FollowService,
    LikeService,
    MediaService,
    TweetService,
    UserService,
)
from .utils import return_exception

__all__ = ["get_session"]

router = APIRouter()


@router.get(
    path="/tweets",
    response_model=TweetsOutSchema,
    responses={401: {"model": ExceptionOutSchema}, 404: {"model": ExceptionOutSchema}},
)
async def get_tweets(
    session: AsyncSession = Depends(get_session),
    api_key: str = Header(default=..., alias="api-key"),
) -> TweetsOutSchema | JSONResponse:
    """
    Получить список твитов пользователя и его подписок.

    Параметры:
        session (AsyncSession): Сессия базы данных.
        api_key (str): API ключ пользователя, передаваемый в заголовке.

    Возвращает:
        TweetsOutSchema: Список твитов.

    Ошибки:
        401: Пользователь не найден.
    """
    result = await TweetService(session=session, api_key=api_key).get()

    if result == 401:
        return return_exception(
            status_code=401,
            error_type="Unauthorized",
            error_message="Пользователь не найден",
        )
    elif isinstance(result, TweetsOutSchema):
        return result.model_dump()
    else:
        return return_exception(
            status_code=500,
            error_type="Error",
            error_message="Unexpected result type",
        )


@router.post(
    path="/tweets",
    response_model=TweetOutSchema,
    responses={401: {"model": ExceptionOutSchema}, 404: {"model": ExceptionOutSchema}},
    status_code=201,
)
async def add_tweet(
    tweet_data: TweetInSchema,
    session: AsyncSession = Depends(get_session),
    api_key: str = Header(default=..., alias="api-key"),
) -> TweetOutSchema | JSONResponse:
    """
    Добавить новый твит.

    Параметры:
        tweet_data (TweetInSchema): Данные о твите.
        session (AsyncSession): Сессия базы данных.
        api_key (str): API ключ пользователя, передаваемый в заголовке.

    Возвращает:
        TweetOutSchema: Созданный твит.

    Ошибки:
        401: Пользователь не найден.
        404: Файл не найден.
    """
    result = await TweetService(session=session, api_key=api_key).post(
        tweet_data=tweet_data
    )

    if result == 401:
        return return_exception(
            status_code=401,
            error_type="Unauthorized",
            error_message="Пользователь не найден",
        )
    elif result == 404:
        return return_exception(
            status_code=404,
            error_type="NotFound",
            error_message="Файл не найден",
        )
    elif isinstance(result, TweetOutSchema):
        return result.model_dump()
    else:
        return return_exception(
            status_code=500,
            error_type="Error",
            error_message="Unexpected result type",
        )


@router.delete(
    path="/tweets/{tweet_id}",
    response_model=SuccessOutSchema,
    responses={
        401: {"model": ExceptionOutSchema},
        403: {"model": ExceptionOutSchema},
        404: {"model": ExceptionOutSchema},
    },
)
async def delete_tweet(
    tweet_id: int,
    session: AsyncSession = Depends(get_session),
    api_key: str = Header(default=..., alias="api-key"),
) -> SuccessOutSchema | JSONResponse:
    """
    Удалить твит по идентификатору.

    Параметры:
        tweet_id (int): Идентификатор твита, который необходимо удалить.
        session (AsyncSession): Сессия базы данных.
        api_key (str): API ключ пользователя, передаваемый в заголовке.

    Возвращает:
        SuccessOutSchema: Результат удаления твита.

    Ошибки:
        401: Пользователь не найден.
        403: Недостаточно прав для удаления твита.
        404: Твит не найден.
    """
    result = await TweetService(session=session, api_key=api_key).delete(
        tweet_id=tweet_id
    )

    if result == 401:
        return return_exception(
            status_code=401,
            error_type="Unauthorized",
            error_message="Пользователь не найден",
        )
    elif result == 403:
        return return_exception(
            status_code=403,
            error_type="Forbidden",
            error_message="Недостаточно прав",
        )
    elif result == 404:
        return return_exception(
            status_code=404,
            error_type="NotFound",
            error_message="Твит не найден",
        )
    elif isinstance(result, SuccessOutSchema):
        return result.model_dump()
    else:
        return return_exception(
            status_code=500,
            error_type="Error",
            error_message="Unexpected result type",
        )


@router.post(
    path="/tweets/{tweet_id}/likes",
    response_model=SuccessOutSchema,
    responses={
        400: {"model": ExceptionOutSchema},
        401: {"model": ExceptionOutSchema},
        404: {"model": ExceptionOutSchema},
    },
    status_code=201,
)
async def like_tweet(
    tweet_id: int,
    session: AsyncSession = Depends(get_session),
    api_key: str = Header(default=..., alias="api-key"),
) -> SuccessOutSchema | JSONResponse:
    """
    Поставить лайк на твит.

    Параметры:
        tweet_id (int): Идентификатор твита, на который ставится лайк.
        session (AsyncSession): Сессия базы данных.
        api_key (str): API ключ пользователя, передаваемый в заголовке.

    Возвращает:
        SuccessOutSchema: Результат операции.

    Ошибки:
        400: Лайк уже поставлен.
        401: Пользователь не найден.
        404: Твит не найден.
    """
    result = await LikeService(session=session, api_key=api_key).post(tweet_id=tweet_id)

    if result == 400:
        return return_exception(
            status_code=400,
            error_type="LikeError",
            error_message="Лайк уже стоит",
        )
    elif result == 401:
        return return_exception(
            status_code=401,
            error_type="Unauthorized",
            error_message="Пользователь не найден",
        )
    elif result == 404:
        return return_exception(
            status_code=404,
            error_type="NotFound",
            error_message="Твит не найден",
        )
    elif isinstance(result, SuccessOutSchema):
        return result.model_dump()
    else:
        return return_exception(
            status_code=500,
            error_type="Error",
            error_message="Unexpected result type",
        )


@router.delete(
    path="/tweets/{tweet_id}/likes",
    response_model=SuccessOutSchema,
    responses={401: {"model": ExceptionOutSchema}, 404: {"model": ExceptionOutSchema}},
)
async def dislike_tweet(
    tweet_id: int,
    session: AsyncSession = Depends(get_session),
    api_key: str = Header(default=..., alias="api-key"),
) -> SuccessOutSchema | JSONResponse:
    """
    Убрать лайк с твита.

    Параметры:
        tweet_id (int): Идентификатор твита, с которого убирается лайк.
        session (AsyncSession): Сессия базы данных.
        api_key (str): API ключ пользователя, передаваемый в заголовке.

    Возвращает:
        SuccessOutSchema: Результат операции.

    Ошибки:
        401: Пользователь не найден.
        404: Лайк не найден.
    """
    result = await LikeService(session=session, api_key=api_key).delete(
        tweet_id=tweet_id
    )

    if result == 401:
        return return_exception(
            status_code=401,
            error_type="Unauthorized",
            error_message="Пользователь не найден",
        )
    elif result == 404:
        return return_exception(
            status_code=404,
            error_type="NotFound",
            error_message="Твит не найден",
        )
    elif isinstance(result, SuccessOutSchema):
        return result.model_dump()
    else:
        return return_exception(
            status_code=500,
            error_type="Error",
            error_message="Unexpected result type",
        )


@router.post(
    path="/medias",
    response_model=MediaOutSchema,
    responses={
        400: {"model": ExceptionOutSchema},
        401: {"model": ExceptionOutSchema},
        404: {"model": ExceptionOutSchema},
    },
    status_code=201,
)
async def add_media(
    file: UploadFile,
    session: AsyncSession = Depends(get_session),
    api_key: str = Header(default=..., alias="api-key"),
) -> MediaOutSchema | JSONResponse:
    """
    Добавить медиафайл.

    Параметры:
        file (UploadFile): Загружаемый файл.
        session (AsyncSession): Сессия базы данных.
        api_key (str): API ключ пользователя, передаваемый в заголовке.

    Возвращает:
        MediaOutSchema: Созданный медиафайл.

    Ошибки:
        400: Файл превышает максимальный размер (5 МБ по умолчанию).
        401: Пользователь не найден.
        404: Файл не найден.
    """
    result = await MediaService(session=session, api_key=api_key).post(file=file)

    if result == 400:
        return return_exception(
            status_code=400,
            error_type="FileError",
            error_message="Максимальный размер файла не должен превышать {MAX_FILE_SIZE_MB} МБ".format(
                MAX_FILE_SIZE_MB=MAX_FILE_SIZE_MB
            ),
        )
    elif result == 401:
        return return_exception(
            status_code=401,
            error_type="Unauthorized",
            error_message="Пользователь не найден",
        )
    elif result == 404:
        return return_exception(
            status_code=404,
            error_type="NotFound",
            error_message="Файл не найден",
        )
    elif isinstance(result, MediaOutSchema):
        return result.model_dump()
    else:
        return return_exception(
            status_code=500,
            error_type="Error",
            error_message="Unexpected result type",
        )


@router.get(
    path="/users/me",
    response_model=SuccessOutUserSchema,
    responses={401: {"model": ExceptionOutSchema}},
)
async def get_profile_my(
    session: AsyncSession = Depends(get_session),
    api_key: str = Header(default=..., alias="api-key"),
) -> SuccessOutUserSchema | JSONResponse:
    """
    Получить профиль текущего пользователя.

    Параметры:
        session (AsyncSession): Сессия базы данных.
        api_key (str): API ключ пользователя, передаваемый в заголовке.

    Возвращает:
        SuccessOutUserSchema: Данные профиля пользователя.

    Ошибки:
        401: Пользователь не найден.
    """
    result = await UserService(session=session, api_key=api_key).get()

    if result == 401:
        return return_exception(
            status_code=401,
            error_type="Unauthorized",
            error_message="Пользователь не найден",
        )
    elif isinstance(result, SuccessOutUserSchema):
        return result.model_dump()
    else:
        return return_exception(
            status_code=500,
            error_type="Error",
            error_message="Unexpected result type",
        )


@router.get(
    path="/users/{user_id}",
    response_model=SuccessOutUserSchema,
    responses={401: {"model": ExceptionOutSchema}},
)
async def get_profile_by_id(
    user_id: int,
    session: AsyncSession = Depends(get_session),
) -> SuccessOutUserSchema | JSONResponse:
    """
    Получить профиль пользователя по его идентификатору.

    Параметры:
        user_id (int): Идентификатор пользователя, чей профиль нужно получить.
        session (AsyncSession): Сессия базы данных.

    Возвращает:
        SuccessOutUserSchema: Данные профиля пользователя.

    Ошибки:
        401: Пользователь не найден.
    """
    result = await UserService(session=session).get(user_id=user_id)

    if result == 401:
        return return_exception(
            status_code=401,
            error_type="Unauthorized",
            error_message="Пользователь не найден",
        )
    elif isinstance(result, SuccessOutUserSchema):
        return result.model_dump()
    else:
        return return_exception(
            status_code=500,
            error_type="Error",
            error_message="Unexpected result type",
        )


@router.post(
    path="/users/{user_id}/follow",
    response_model=SuccessOutSchema,
    responses={
        400: {"model": ExceptionOutSchema},
        401: {"model": ExceptionOutSchema},
        404: {"model": ExceptionOutSchema},
        409: {"model": ExceptionOutSchema},
    },
    status_code=201,
)
async def follow_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    api_key: str = Header(default=..., alias="api-key"),
) -> SuccessOutSchema | JSONResponse:
    """
    Подписаться на пользователя.

    Параметры:
        user_id (int): Идентификатор пользователя, на которого нужно подписаться.
        session (AsyncSession): Сессия базы данных.
        api_key (str): API ключ пользователя, передаваемый в заголовке.

    Возвращает:
        SuccessOutSchema: Результат операции.

    Ошибки:
        400: Невозможно подписаться на себя.
        401: Пользователь не найден.
        404: Пользователь для подписки не найден.
        409: Пользователь уже подписан на данного пользователя.
    """
    result = await FollowService(session=session, api_key=api_key).post(user_id=user_id)

    if result == 400:
        return return_exception(
            status_code=400,
            error_type="FollowError",
            error_message="Вы не можете подписаться на себя",
        )
    elif result == 401:
        return return_exception(
            status_code=401,
            error_type="Unauthorized",
            error_message="Пользователь не найден",
        )
    elif result == 404:
        return return_exception(
            status_code=404,
            error_type="NotFound",
            error_message="Пользователь для подписки не найден",
        )
    elif result == 409:
        return return_exception(
            status_code=409,
            error_type="FollowError",
            error_message="Вы уже подписаны на пользователя",
        )
    elif isinstance(result, SuccessOutSchema):
        return result.model_dump()
    else:
        return return_exception(
            status_code=500,
            error_type="Error",
            error_message="Unexpected result type",
        )


@router.delete(
    path="/users/{user_id}/follow",
    response_model=SuccessOutSchema,
    responses={
        400: {"model": ExceptionOutSchema},
        401: {"model": ExceptionOutSchema},
        404: {"model": ExceptionOutSchema},
    },
)
async def unfollow_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    api_key: str = Header(default=..., alias="api-key"),
) -> SuccessOutSchema | JSONResponse:
    """
    Убрать подписку на пользователя.

    Параметры:
        user_id (int): Идентификатор пользователя, от которого нужно отписаться.
        session (AsyncSession): Сессия базы данных.
        api_key (str): API ключ пользователя, передаваемый в заголовке.

    Возвращает:
        SuccessOutSchema: Результат операции.

    Ошибки:
        400: Невозможно отписаться от себя.
        401: Пользователь не найден.
        404: Подписка не найдена.
    """
    result = await FollowService(session=session, api_key=api_key).delete(
        user_id=user_id
    )

    if result == 400:
        return return_exception(
            status_code=400,
            error_type="FollowError",
            error_message="Вы не можете отписаться от себя",
        )
    elif result == 401:
        return return_exception(
            status_code=401,
            error_type="Unauthorized",
            error_message="Пользователь не найден",
        )
    elif result == 404:
        return return_exception(
            status_code=404,
            error_type="NotFound",
            error_message="Подписка не найдена",
        )
    elif isinstance(result, SuccessOutSchema):
        return result.model_dump()
    else:
        return return_exception(
            status_code=500,
            error_type="Error",
            error_message="Unexpected result type",
        )
