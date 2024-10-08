from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class TweetInSchema(BaseModel):
    """
    Схема входящих данных твита.

    Атрибуты:
        content (str): Содержимое твита.
        tweet_media_ids (Optional[list[int]]): Список идентификаторов вложений.
    """

    content: str = Field(default=..., alias="tweet_data")
    tweet_media_ids: Optional[list[int]] = Field(default_factory=list)

    model_config = ConfigDict(
        from_attributes=True,
    )


class SuccessOutSchema(BaseModel):
    """
    Схема успешного ответа.

    Атрибуты:
        result (bool): Флаг успешности операции.
    """

    result: bool = Field(default=True, exclude=False)


class ExceptionOutSchema(BaseModel):
    """
    Схема ответа с ошибкой.

    Атрибуты:
        result (bool): Флаг успешности операции (всегда False).
        error_type (str): Тип ошибки.
        error_message (str): Сообщение об ошибке.
    """

    result: bool = Field(default=False, exclude=False)
    error_type: str
    error_message: str


class TweetOutSchema(SuccessOutSchema):
    """
    Схема выходящих данных твита.

    Атрибуты:
        id (int): Идентификатор твита.
    """

    id: int = Field(default=..., alias="tweet_id")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )


class AuthorSchema(BaseModel):
    """
    Схема автора твита.

    Атрибуты:
        id (int): Идентификатор автора.
        name (str): Имя автора.
    """

    id: int
    name: str


class LikeSchema(BaseModel):
    """
    Схема лайка на твит.

    Атрибуты:
        user_id (int): Идентификатор пользователя, поставившего лайк.
        name (str): Имя пользователя, поставившего лайк.
    """

    user_id: int
    name: str


class TweetOutForListSchema(BaseModel):
    """
    Схема выходящих данных твита для списка твитов.

    Атрибуты:
        id (int): Идентификатор твита.
        content (str): Содержимое твита.
        attachments (Optional[list[str]]): Список вложений (например, изображений).
        author (AuthorSchema): Автор твита.
        likes (list[LikeSchema]): Список лайков на твит.
    """

    id: int
    content: str
    attachments: Optional[list[str]] = None
    author: AuthorSchema
    likes: list[LikeSchema]


class TweetsOutSchema(SuccessOutSchema):
    """
    Схема выходящих данных списка твитов.

    Атрибуты:
        tweets (list[TweetOutForListSchema]): Список твитов.
    """

    tweets: list[TweetOutForListSchema] = Field(default_factory=list)
    # default_factory=list нужно для того, чтобы список создавался для каждого экзепляра,
    # а не использовался один для всех


class UserSchema(BaseModel):
    """
    Базовая схема пользователя.

    Атрибуты:
        id (int): Идентификатор пользователя.
        name (str): Имя пользователя.
    """

    id: int
    name: str


class UserOutSchema(UserSchema):
    """
    Схема выходящих данных пользователя.

    Атрибуты:
        followers (list[UserSchema]): Список подписчиков пользователя.
        following (list[UserSchema]): Список пользователей, на которых подписан данный пользователь.
    """

    followers: list[UserSchema]
    following: list[UserSchema]

    model_config = ConfigDict(
        from_attributes=True,
    )


class SuccessOutUserSchema(SuccessOutSchema):
    """
    Схема успешного ответа с данными пользователя.

    Атрибуты:
        user (UserOutSchema): Данные пользователя.
    """

    user: UserOutSchema


class MediaOutSchema(SuccessOutSchema):
    """
    Схема выходящих данных медиафайла.

    Атрибуты:
        id (int): Идентификатор медиафайла.
    """

    id: int = Field(..., alias="media_id")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )
