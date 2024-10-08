from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AvailableLearningOutcomes, CellData, CourseViewSet, LearningObjectViewSet, UpdateLearningObjectsView

router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'learning-objects', LearningObjectViewSet)

urlpatterns = [
    path('available_lo/', AvailableLearningOutcomes.as_view()),
    path('update_learning_objects/', UpdateLearningObjectsView.as_view(), name='update_learning_objects'),
    path('cell/<cell_id>/', CellData.as_view()),
    path('', include(router.urls)),
]