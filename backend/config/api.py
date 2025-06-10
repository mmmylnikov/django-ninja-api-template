from django.contrib.auth import get_user_model
from django.http import HttpRequest, JsonResponse
from events.api import router as events_router
from ninja import NinjaAPI
from ninja.security import HttpBearer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import (
    AuthenticationFailed,
    InvalidToken,
)
from users.api import jwt_router
from users.api import router as users_router


User = get_user_model()


class AuthJWT(HttpBearer):
    """Authentication class that implements JWT token validation."""

    def authenticate(self, request: HttpRequest, token: str) -> User | None:  # type: ignore
        """Validates the JWT token provided in the Authorization header."""
        authenticator = JWTAuthentication()
        validated = authenticator.authenticate(request)
        if not validated:
            return None
        user, _ = validated
        return user


api = NinjaAPI()


@api.exception_handler(InvalidToken)
def jwt_invalid_token_handler(
    request: HttpRequest, exc: Exception
) -> JsonResponse:
    return JsonResponse({'detail': 'Invalid token'}, status=403)


@api.exception_handler(AuthenticationFailed)
def jwt_auth_failed_handler(
    request: HttpRequest, exc: Exception
) -> JsonResponse:
    return JsonResponse({'detail': str(exc)}, status=403)


api.add_router('/users/', users_router)
api.add_router('/auth/', jwt_router)
api.add_router(
    '/events/',
    events_router,
    auth=AuthJWT(),
)
