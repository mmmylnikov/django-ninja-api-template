from django.http import HttpRequest
from ninja import Router
from ninja.errors import HttpError
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from users.schemas import (
    AuthTokenOut,
    RefreshTokenIn,
    UserLoginIn,
    UserOut,
    UserRegistrationIn,
)
from users.services import (
    AuthenticationError,
    PasswordValidationError,
    UserAlreadyExistsError,
    authenticate_user,
    register_user,
)


router = Router(tags=['users'])


@router.post('/register', response=UserOut)
def register_user_api(
    request: HttpRequest, user_in: UserRegistrationIn
) -> UserOut:
    """
    Registers a new user.

    Accepts user registration data: username, email,
    password, password confirmation, first and last name. Checks the uniqueness
    of the name the user's name and email address, as well as the password's
    compliance with security requirements. If the registration was successful,
    it returns the created user.
    """
    user_data = user_in.dict()
    user_data.pop('confirm_password')
    try:
        return UserOut.from_orm(register_user(**user_data))
    except UserAlreadyExistsError as error:
        raise HttpError(400, str(error)) from error
    except PasswordValidationError as error:
        raise HttpError(400, str(error)) from error
    except Exception as error:
        raise HttpError(500, f'Ошибка регистрации: {error}') from error


jwt_router = Router(tags=['auth'])


@jwt_router.post('/login', response=AuthTokenOut)
def login_jwt_api(request: HttpRequest, user_data: UserLoginIn) -> AuthTokenOut:
    """
    User authentication with receipt of JWT tokens.

    Accepts username and password, returns access and refresh tokens.
    """
    try:
        user = authenticate_user(
            request, user_data.username, user_data.password
        )
    except AuthenticationError as error:
        raise HttpError(400, str(error)) from error
    else:
        refresh = RefreshToken.for_user(user)
        return AuthTokenOut(
            access=str(refresh.access_token),
            refresh=str(refresh),
        )


@jwt_router.post('/token/refresh', response=AuthTokenOut)
def token_refresh(
    request: HttpRequest, user_data: RefreshTokenIn
) -> AuthTokenOut:
    """
    Updating an access token using a refresh token.
    """
    try:
        refresh = RefreshToken(user_data.refresh)  # type: ignore
    except TokenError as error:
        raise HttpError(400, f'Invalid refresh token: {error}') from error
    else:
        return AuthTokenOut(
            access=str(refresh.access_token), refresh=str(refresh)
        )
