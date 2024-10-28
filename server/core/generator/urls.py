from django.urls import path

from .views import OptimizeLearningObjects

urlpatterns = [
    path('optimize/', OptimizeLearningObjects.as_view()),
]