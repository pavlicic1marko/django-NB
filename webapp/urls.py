from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"news", views.NewsViewSet, basename="news")

urlpatterns = [
    path("home1/", views.home1, name="home1"),
    path("", views.home, name="home"),
    path("about-us/", views.about_us, name="about_us"),
    path("products/", views.products, name="products"),
    path("chat/", views.chat, name="chat"),
    path("contact/", views.contact, name="contact"),
    path("schedule-meeting/", views.contact, name="schedule_meeting"),
    path("blog/", views.blog, name="blog"),
    path("news/", views.blog, name="news"),
    path("api/", include(router.urls)),
    path("api/chat/threads/", views.start_conversation, name="start_conversation"),
    path("api/chat/threads/<int:thread_id>/", views.get_conversation, name="get_conversation"),
    path("api/chat/threads/<int:thread_id>/questions/", views.add_question, name="add_question"),
    path("api/chat/threads/<int:thread_id>/end/", views.end_conversation, name="end_conversation"),
]