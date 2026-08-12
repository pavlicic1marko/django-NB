from django.urls import path
from . import views

urlpatterns = [
    path("home1/", views.home1, name="home1"),
    path("home/", views.home, name="home"),
    path("about-us/", views.about_us, name="about_us"),
    path("products/", views.products, name="products"),
    path("contact/", views.contact, name="contact"),
    path("schedule-meeting/", views.contact, name="schedule_meeting"),

]