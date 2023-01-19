from django.urls import path
from .views import RegisterView, LoginView, LogoutView, UploadFile

urlpatterns = [
    path('register', RegisterView.as_view()),
    path('login', LoginView.as_view()),
    path('logout', LogoutView.as_view()),
    path('upload', UploadFile.as_view()),
]