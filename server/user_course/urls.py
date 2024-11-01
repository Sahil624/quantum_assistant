from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AIInteractionViewSet,
    ActivityLogViewSet,
    AssignmentSubmissionViewSet,
    AvailableLearningOutcomes,
    CellData,
    CourseViewSet,
    FileDownloadAPIView,
    LearningObjectViewSet,
    MetaDataView,
    UpdateLearningObjectsView,
)

router = DefaultRouter()
router.register(r"courses", CourseViewSet)
router.register(r"learning-objects", LearningObjectViewSet)
router.register(r"activity-logs", ActivityLogViewSet)
router.register(r"assignment-submissions", AssignmentSubmissionViewSet)
router.register(r"ai-interactions", AIInteractionViewSet)

urlpatterns = [
    path("available_lo/", AvailableLearningOutcomes.as_view()),
    path("meta/", MetaDataView.as_view()),
    path(
        "update_learning_objects/",
        UpdateLearningObjectsView.as_view(),
        name="update_learning_objects",
    ),
    path("cell/<cell_id>/", CellData.as_view()),
    path('download/<str:cell_id>/', FileDownloadAPIView.as_view(), name='file-download'),
    path("", include(router.urls)),
]
