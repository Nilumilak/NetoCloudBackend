from django.urls import path
from .views import StorageListView, StorageRetrieveView

urlpatterns = [
    path('storages/', StorageListView.as_view()),
    path('storages/<int:pk>/', StorageRetrieveView.as_view()),
]
