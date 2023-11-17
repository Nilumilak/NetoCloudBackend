from django.contrib import admin
from django.urls import include, path

from files.views import FileDownloadView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("<str:url>/", FileDownloadView.as_view()),
    path("download/<str:url>/", FileDownloadView.as_view()),
    path("api/v1/", include("api.urls")),
    path("api/v1/", include("user.urls")),
    path("api/v1/", include("storage.urls")),
    path("api/v1/", include("files.urls")),
]
