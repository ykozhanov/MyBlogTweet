from factory import LazyFunction
from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker

from app.server.models.models import User

fake = Faker()


class UserFactory(SQLAlchemyModelFactory):  # type: ignore[type-arg]
    """
    Фабрика для создания объектов пользователя.

    Использует SQLAlchemy для создания экземпляров модели User и Faker для генерации случайных данных.

    Атрибуты:
        name (str): Имя пользователя, генерируемое с помощью Faker.
        api_key (str): Уникальный API ключ пользователя, генерируемый с помощью Faker.
    """

    class Meta:
        model = User
        sqlalchemy_session_factory = None
        exclude = ("id",)
        # Фабрика не будет генерировать значение для поля id, вместо этого оно будет генерироваться самой базой данных.

    # Если не использовать LazyFunction, то значения сгенерируются один раз и будут одинаковые
    name = LazyFunction(fake.user_name)
    api_key = LazyFunction(fake.sha256)
