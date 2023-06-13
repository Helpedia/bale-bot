from django.urls import path
from .views import ReaderAPI


urlpatterns = [
    path("update/", ReaderAPI.as_view()),
]