import os

from fastapi.responses import JSONResponse
from models.models import Tweet, User
from schemas.schemas import ExceptionOutSchema


async def create_path_img(user: User, filename: str, extension: str) -> str:
    """
    Создает уникальный путь для сохранения изображения, загружаемого пользователем.

    Параметры:
        user (User): Объект пользователя.
        filename (str): Имя файла изображения.
        extension (str): Расширение файла изображения.

    Возвращает:
        str: Уникальный путь для сохранения изображения.
    """
    counter = 1

    base_path = "./images/{user_id}".format(user_id=user.id)
    os.makedirs(base_path, exist_ok=True)

    path_img = "{base_path}/{filename}{extension}".format(
        base_path=base_path,
        filename=filename,
        extension=extension,
    )

    while os.path.exists(path_img):
        path_img = "{base_path}/{filename}_{counter}{extension}".format(
            base_path=base_path,
            filename=filename,
            extension=extension,
            counter=counter,
        )

        counter += 1

    return path_img


def sorted_tweets(tweets_list: list[Tweet], following_users: list[int]) -> list[Tweet]:
    """
    Сортирует список твитов в порядке убывания по следующим критериям:
    1. Твиты, на которые подписан пользователь, идут первыми (в приоритете лайк пользователя, так настроен роут).
    2. Твиты с большим количеством лайков идут выше.

    Параметры:
        tweets_list (list[Tweet]): Список твитов для сортировки.
        following_users (list[int]): Список идентификаторов пользователей, на которых подписан текущий пользователь.

    Возвращает:
        list[Tweet]: Отсортированный список твитов.
    """
    return sorted(
        tweets_list,
        key=lambda t: (
            any(like.user_id in following_users for like in t.likes),
            len(t.likes),
        ),
        reverse=True,
    )


def return_exception(
    error_type: str, error_message: str, status_code: int
) -> JSONResponse:
    """
    Возвращает JSON ответ с ошибкой.

    Параметры:
        error_type (str): Тип ошибки.
        error_message (str): Сообщение об ошибке.
        status_code (int): Код статуса HTTP ответа (по умолчанию 404).

    Возвращает:
        JSONResponse: Ответ с ошибкой в формате JSON.
    """
    return JSONResponse(
        status_code=status_code,
        content=ExceptionOutSchema(
            error_type=error_type,
            error_message=error_message,
        ).model_dump(),
    )
