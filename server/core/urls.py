from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import ConversationViewSet

router = DefaultRouter()
router.register('', ConversationViewSet)

urlpatterns = [
    path('conversation/', include(router.urls)),
    path('assistant/', include('core.assistant.urls')),
    path('generator/', include('core.generator.urls')),
]