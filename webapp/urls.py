from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"news", views.NewsViewSet, basename="news")

urlpatterns = [
    path("home1/", views.home1, name="home1"),
    path("home/", views.home, name="home"),
    path("about-us/", views.about_us, name="about_us"),
    path("products/", views.products, name="products"),
    path("contact/", views.contact, name="contact"),
    path("schedule-meeting/", views.contact, name="schedule_meeting"),
    path("news/", views.news, name="news"),
    path("api/", include(router.urls)),
]