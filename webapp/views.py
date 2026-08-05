from django.http import HttpResponse


def home(request):
    return HttpResponse("Hello from my first Django app!")
