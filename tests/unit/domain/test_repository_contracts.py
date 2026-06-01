import inspect

from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.database.repositories.sqlalchemy_user_repo import (
    SQLAlchemyUserRepository,
)


def test_user_repository_create_contract_matches_implementation():
    abc_signature = inspect.signature(UserRepository.create)
    impl_signature = inspect.signature(SQLAlchemyUserRepository.create)

    assert list(abc_signature.parameters) == list(impl_signature.parameters)

    hashed_password_param = abc_signature.parameters["hashed_password"]
    assert hashed_password_param.kind is inspect.Parameter.KEYWORD_ONLY
    assert hashed_password_param.default is inspect._empty


def test_user_repository_methods_are_async():
    for method_name in ["find_by_id", "find_by_email", "find_all", "list_by_department", "create", "update", "delete"]:
        assert inspect.iscoroutinefunction(getattr(UserRepository, method_name))
        assert inspect.iscoroutinefunction(getattr(SQLAlchemyUserRepository, method_name))


def test_user_repository_is_abstract():
    abstract_methods = UserRepository.__abstractmethods__
    assert {"find_by_id", "find_by_email", "find_all", "list_by_department", "create", "update", "delete"} <= abstract_methods