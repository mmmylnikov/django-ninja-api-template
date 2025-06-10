from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpRequest


class UserAlreadyExistsError(Exception):
    """Exception raised when attempting to create a user that already exists."""


class PasswordValidationError(Exception):
    """Exception raised when password validation fails."""


class AuthenticationError(Exception):
    """Exception raised when authentication fails."""


@transaction.atomic
def register_user(
    username: str,
    email: str,
    password: str,
    first_name: str,
    last_name: str,
) -> User:
    if User.objects.filter(username=username).exists():
        raise UserAlreadyExistsError(
            f"The user named '{username}' already exists"
        )
    if User.objects.filter(email=email).exists():
        raise UserAlreadyExistsError(
            f"The user with the email '{email}' has already been registered"
        )

    try:
        validate_password(password)
    except ValidationError as error:
        raise PasswordValidationError(str(error)) from error

    return User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
    )


def get_user(user_id: int) -> User:
    return User.objects.get(id=user_id)


def authenticate_user(
    request: HttpRequest, username: str, password: str
) -> User:
    user = authenticate(username=username, password=password)
    if user is None:
        raise AuthenticationError('Invalid username or password')
    login(request, user)
    return user
