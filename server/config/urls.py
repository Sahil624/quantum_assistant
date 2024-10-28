from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "QUINTET Admin"
admin.site.index_title = "QUINTET Features"
admin.site.site_title = "QUINTET Admin"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('api.urls')),
]
