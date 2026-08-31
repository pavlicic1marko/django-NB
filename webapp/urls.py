from django.urls import path
from django.utils.translation import gettext_lazy as _

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path(_("about-us/"), views.about_us, name="about_us"),
    path(_("products/"), views.products, name="products"),
    path(_("chat/"), views.chat, name="chat"),
    path(_("contact/"), views.contact, name="contact"),
    path(_("schedule-meeting/"), views.contact, name="schedule_meeting"),
    path(_("blog/"), views.blog, name="blog"),
    path(_("news/"), views.blog, name="news"),
    path(_("news/<slug:slug>/"), views.news_detail, name="news_detail"),
]