from django.urls import path

from .views import DownloadUpload, ShowFile


urlpatterns = [
    path('files/', DownloadUpload.as_view()),
    path('files/download/<str:url>', ShowFile.as_view()),
]
