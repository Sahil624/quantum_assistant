# quantum_assistant/routing.py

from django.urls import re_path
from .assistant import consumer

websocket_urlpatterns = [
    re_path(r'ws/assistant/(?P<conversation_id>\w+)/$', consumer.QuantumAssistantConsumer.as_asgi()),
    re_path(r'ws/assistant/', consumer.QuantumAssistantConsumer.as_asgi()),
]