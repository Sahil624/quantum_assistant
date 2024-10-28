
from django.urls import include, path

from .view import AssistantView


urlpatterns = [
    path('<conversation_id>/', AssistantView.as_view()),
]