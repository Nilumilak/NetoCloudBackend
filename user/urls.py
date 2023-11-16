from django.urls import path

from .views import UserDeleteView, UserDetailedView, UserListCreateView, UserUpdateView

urlpatterns = [
    path("users/", UserListCreateView.as_view()),
    path("users/<int:pk>/", UserDetailedView.as_view()),
    path("users/update/<int:pk>/", UserUpdateView.as_view()),
    path("users/delete/<int:pk>/", UserDeleteView.as_view()),
]
