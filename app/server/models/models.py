from sqlalchemy import ARRAY, ForeignKey, Integer, String
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declarative_base,
    mapped_column,
    relationship,
)

# Создаю тут, чтобы не было проблем с циклическим импортом
Base: DeclarativeBase = declarative_base()


class Tweet(Base):
    """
    Модель для представления твита в базе данных.

    Атрибуты:
        id (int): Уникальный идентификатор твита.
        user_id (int): Идентификатор пользователя, который создал твит.
        content (str): Содержимое твита (максимум 280 символов).
        attachments (list[str]): Список идентификаторов вложений.

        user (User): Связь с моделью User, представляющая пользователя, который создал твит.
        likes (list[Like]): Связь с моделью Like, представляющая лайки на твит.
    """

    __tablename__ = "tweets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
    content: Mapped[str] = mapped_column(String(280), nullable=False)
    attachments: Mapped[list[str]] = mapped_column(ARRAY(String))

    # lazy="joined" позволяет подгружать данные о пользователе сразу вместе с твитом
    user: Mapped["User"] = relationship("User", back_populates="tweets", lazy="joined")
    likes: Mapped[list["Like"]] = relationship(
        "Like", back_populates="tweet", lazy="subquery", cascade="all, delete-orphan"
    )


class Media(Base):
    """
    Модель для представления медиафайлов в базе данных.

    Атрибуты:
        id (int): Уникальный идентификатор медиафайла.
        path_file (str): Путь к файлу медиа.
        user_id (int): Идентификатор пользователя, которому принадлежит медиафайл.
    """

    __tablename__ = "medias"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    path_file: Mapped[str] = mapped_column(String, nullable=False)
    user_id: Mapped[str] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )


class User(Base):
    """
    Модель для представления пользователя в базе данных.

    Атрибуты:
        id (int): Уникальный идентификатор пользователя.
        name (str): Никнейм пользователя (уникально).
        api_key (str): Уникальный ключ API для пользователя.

        tweets (list[Tweet]): Связь с моделью Tweet, представляющая твиты пользователя.
        likes (list[Like]): Связь с моделью Like, представляющая лайки пользователя.
        followers (list[Follow]): Связь с моделью Follow, представляющая подписчиков пользователя.
        following (list[Follow]): Связь с моделью Follow, представляющая пользователей, на которых подписан пользователь.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    api_key: Mapped[str] = mapped_column(String, unique=True, index=True)

    tweets: Mapped[list["Tweet"]] = relationship("Tweet", back_populates="user")
    likes: Mapped[list["Like"]] = relationship("Like", back_populates="user")

    followers: Mapped[list["Follow"]] = relationship(
        "Follow",
        back_populates="followed",
        foreign_keys="[Follow.followed_id]",
        lazy="selectin",
    )
    following: Mapped[list["Follow"]] = relationship(
        "Follow",
        back_populates="follower",
        foreign_keys="[Follow.follower_id]",
        lazy="selectin",
    )


class Follow(Base):
    """
    Модель для представления подписок пользователей в базе данных.

    Атрибуты:
        follower_id (int): Идентификатор пользователя, который подписывается.
        followed_id (int): Идентификатор пользователя, на которого подписываются.

        follower (User): Связь с моделью User, представляющая подписчика.
        followed (User): Связь с моделью User, представляющая подписанного пользователя.
    """

    __tablename__ = "followers"

    follower_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), primary_key=True
    )
    followed_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), primary_key=True
    )

    follower: Mapped["User"] = relationship("User", foreign_keys=[follower_id])
    followed: Mapped["User"] = relationship("User", foreign_keys=[followed_id])


class Like(Base):
    """
    Модель для представления лайков на твиты в базе данных.

    Атрибуты:
        tweet_id (int): Идентификатор твита, на который поставлен лайк.
        user_id (int): Идентификатор пользователя, который поставил лайк.

        tweet (Tweet): Связь с моделью Tweet, представляющая лайкнутый твит.
        user (User): Связь с моделью User, представляющая пользователя, который поставил лайк.
    """

    __tablename__ = "likes"

    tweet_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tweets.id"), nullable=False, primary_key=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, primary_key=True
    )

    tweet: Mapped["Tweet"] = relationship("Tweet", back_populates="likes")
    user: Mapped["User"] = relationship("User", back_populates="likes")
