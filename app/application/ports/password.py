from typing import Protocol


class IPasswordService(Protocol):
    """Port để Application layer hash/verify password mà không phụ thuộc thư viện bcrypt cụ thể."""

    def hash(self, plain_password: str) -> str:
        ...

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        ...
