from django.http import HttpResponse
from django.shortcuts import render


def home1(request):
    return HttpResponse("Hello from my first Django app!")



def home(request):
    return render(request, "website/home.html")