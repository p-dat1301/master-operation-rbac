from typing import Protocol


class ITokenService(Protocol):
    """Port để Application layer tạo/đọc access token mà không phụ thuộc thư viện JWT cụ thể."""

    def create_access_token(self, subject: str, claims: dict[str, object] | None = None) -> str:
        ...

    def decode_access_token(self, token: str) -> dict[str, object]:
        ...
