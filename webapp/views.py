from django.http import HttpResponse
from django.shortcuts import render


def home1(request):
    return HttpResponse("Hello from my first Django app!")



def home(request):
    return render(request, "website/home.html")


def about_us(request):
    return render(request, "website/about_us.html")


def products(request):
    return render(request, "website/products.html")


def contact(request):
    return render(request, "website/contact.html")