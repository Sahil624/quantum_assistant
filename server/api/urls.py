from django.urls import include, path

urlpatterns = [
    path('users/', include('users.urls')),
    path('course/', include('user_course.urls')),
    path('core/', include('core.urls')),
]
