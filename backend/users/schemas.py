from typing import Self

from ninja import Schema
from pydantic import EmailStr, Field, model_validator


class UserRegistrationIn(Schema):
    username: str = Field(..., min_length=3, max_length=32)
    email: EmailStr
    password: str = Field(..., min_length=8)
    confirm_password: str
    first_name: str = Field(..., min_length=2)
    last_name: str = Field(..., min_length=2)

    @model_validator(mode='after')
    def check_passwords_match(self) -> Self:
        if self.password != self.confirm_password:
            raise ValueError('Passwords do not match')
        return self


class UserOut(Schema):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str


class UserLoginIn(Schema):
    username: str = Field(..., min_length=3, max_length=32)
    password: str = Field(..., min_length=8)


class AuthTokenOut(Schema):
    access: str
    refresh: str


class RefreshTokenIn(Schema):
    refresh: str
