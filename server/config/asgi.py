"""
ASGI config for config project.
It exposes the ASGI callable as a module-level variable named ``application``.
For more information on this file, see
https://docs.djangoproject.com/en/dev/howto/deployment/asgi/
"""

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

import os

from django.core.asgi import get_asgi_application

from core.routing import websocket_urlpatterns
from .socket_auth import QueryAuthMiddleware

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": QueryAuthMiddleware(URLRouter(websocket_urlpatterns)),
    }
)
