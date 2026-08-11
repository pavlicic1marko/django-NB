from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render

from .models import Message


def home1(request):
    return HttpResponse("Hello from my first Django app!")



def home(request):
    return render(request, "website/home.html")


def about_us(request):
    return render(request, "website/about_us.html")


def products(request):
    return render(request, "website/products.html")


def contact(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        subject = request.POST.get("subject", "").strip()
        message_text = request.POST.get("message", "").strip()

        if not all([name, email, subject, message_text]):
            messages.error(request, "Please complete all fields before sending your message.")
            return render(
                request,
                "website/contact.html",
                {
                    "form_data": {
                        "name": name,
                        "email": email,
                        "subject": subject,
                        "message": message_text,
                    }
                },
            )

        forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        ip_address = forwarded_for.split(",")[0].strip() if forwarded_for else request.META.get("REMOTE_ADDR")

        Message.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message_text,
            ip_address=ip_address,
        )
        messages.success(request, "Thanks! Your message has been sent successfully.")
        return redirect("contact")

    return render(request, "website/contact.html")