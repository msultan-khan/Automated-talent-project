import secrets

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from rest_framework import authentication, exceptions


class ServiceUser(AnonymousUser):
    @property
    def is_authenticated(self) -> bool:
        return True


class BearerApiKeyAuthentication(authentication.BaseAuthentication):
    keyword = "Bearer"

    def authenticate(self, request):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header:
            raise exceptions.AuthenticationFailed("Missing Authorization header.")

        try:
            keyword, api_key = auth_header.split(" ", 1)
        except ValueError as exc:
            raise exceptions.AuthenticationFailed("Invalid Authorization header format.") from exc

        if keyword.lower() != self.keyword.lower():
            raise exceptions.AuthenticationFailed("Authorization header must use Bearer scheme.")

        configured_key = settings.SERVICE_API_KEY.strip()
        if not configured_key:
            raise exceptions.AuthenticationFailed("Server API key is not configured.")

        if not secrets.compare_digest(api_key.strip(), configured_key):
            raise exceptions.AuthenticationFailed("Invalid API key.")

        return ServiceUser(), None
