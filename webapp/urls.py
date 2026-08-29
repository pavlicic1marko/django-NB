from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("about-us/", views.about_us, name="about_us"),
    path("products/", views.products, name="products"),
    path("chat/", views.chat, name="chat"),
    path("contact/", views.contact, name="contact"),
    path("schedule-meeting/", views.contact, name="schedule_meeting"),
    path("blog/", views.blog, name="blog"),
    path("news/", views.blog, name="news"),
    path("news/<int:news_id>/", views.news_detail, name="news_detail"),
]