import logging
from urllib.parse import unquote
from channels.db import database_sync_to_async
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.models import AnonymousUser
from asgiref.sync import sync_to_async

class AsyncJWTAuthentication(JWTAuthentication):
    @sync_to_async
    def get_validated_token(self, raw_token):
        return super().get_validated_token(raw_token)

    @sync_to_async
    def get_user(self, validated_token):
        return super().get_user(validated_token)

async def get_user(jwt_token: str):
    auth = AsyncJWTAuthentication()
    print("===>", jwt_token)
    token = await auth.get_validated_token(jwt_token.encode())
    return await auth.get_user(token)

class QueryAuthMiddleware:
    """
    Custom middleware (insecure) that takes user IDs from the query string.
    """

    def __init__(self, app):
        # Store the ASGI application we were passed
        self.app = app

    async def __call__(self, scope, receive, send):
        # Look up user from query string (you should also do things like
        # checking if it is a valid user ID, or if scope["user"] is already
        # populated).
        print(scope['query_string'])
        try:
            jwt_token = unquote(scope["query_string"].decode())
        except KeyError:
            logging.error(f"A websocket request came without token! {scope['query_string']}")
            scope['user'] = AnonymousUser()
        else:
            scope['user'] = await get_user(jwt_token)

        return await self.app(scope, receive, send)