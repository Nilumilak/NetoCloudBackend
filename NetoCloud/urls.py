from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("api.urls")),
    path("api/v1/", include("user.urls")),
    path("api/v1/", include("storage.urls")),
    path("api/v1/", include("files.urls")),
]
