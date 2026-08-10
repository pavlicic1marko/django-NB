from django.urls import path
from . import views

urlpatterns = [
    path("home1/", views.home1, name="home1"),
    path("home/", views.home, name="home"),

]