from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"news", views.NewsViewSet, basename="news")

urlpatterns = [
    path("chat/threads/", views.start_conversation, name="start_conversation"),
    path("chat/threads/<int:thread_id>/", views.get_conversation, name="get_conversation"),
    path("chat/threads/<int:thread_id>/questions/", views.add_question, name="add_question"),
    path("chat/threads/<int:thread_id>/end/", views.end_conversation, name="end_conversation"),
] + router.urls