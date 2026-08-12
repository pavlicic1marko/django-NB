from datetime import date as dt_date
from datetime import timezone as dt_timezone
from collections import defaultdict

from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from .models import Message, Metting, TIME_SLOT_CHOICES


def _future_booked_slots_by_date():
    utc_today = timezone.now().astimezone(dt_timezone.utc).date()
    slot_order = [slot_value for slot_value, _ in TIME_SLOT_CHOICES]
    slots = defaultdict(set)
    slots[utc_today.isoformat()].update(slot_order)

    for slot_date, slot_time in Metting.objects.filter(date__gt=utc_today).values_list("date", "timeslot"):
        slots[slot_date.isoformat()].add(slot_time)

    return {date_key: [slot for slot in slot_order if slot in slot_values] for date_key, slot_values in slots.items()}


def _render_contact(request, form_data=None, schedule_data=None, schedule_modal_open=False):
    return render(
        request,
        "website/contact.html",
        {
            "form_data": form_data or {},
            "schedule_data": schedule_data or {},
            "schedule_modal_open": schedule_modal_open,
            "booked_slots_by_date": _future_booked_slots_by_date(),
        },
    )


def home1(request):
    return HttpResponse("Hello from my first Django app!")



def home(request):
    return render(request, "website/home.html")


def about_us(request):
    return render(request, "website/about_us.html")


def products(request):
    return render(request, "website/products.html")


def news(request):
    articles = [
        {"title": "Operations briefing: August service update", "date": dt_date(2026, 8, 12)},
        {"title": "New reporting tools available to teams", "date": dt_date(2026, 8, 8)},
        {"title": "Customer support schedule for the holiday period", "date": dt_date(2026, 8, 4)},
        {"title": "Product release notes: workflow improvements", "date": dt_date(2026, 7, 30)},
        {"title": "Planning guide for the next quarter", "date": dt_date(2026, 7, 25)},
        {"title": "Service status review: July highlights", "date": dt_date(2026, 7, 21)},
        {"title": "Security reminder for account administrators", "date": dt_date(2026, 7, 16)},
        {"title": "Team collaboration practices that scale", "date": dt_date(2026, 7, 11)},
        {"title": "Upcoming maintenance window announced", "date": dt_date(2026, 7, 7)},
        {"title": "How we are improving response times", "date": dt_date(2026, 7, 2)},
        {"title": "Community update: June milestones", "date": dt_date(2026, 6, 27)},
        {"title": "Getting started with the latest tools", "date": dt_date(2026, 6, 23)},
    ]
    article_page = Paginator(articles, 10).get_page(request.GET.get("page"))
    return render(request, "website/news.html", {"article_page": article_page})


def contact(request):
    if request.method == "POST":
        if request.POST.get("form_type") == "schedule":
            name = request.POST.get("meeting_name", "").strip()
            email = request.POST.get("meeting_email", "").strip()
            phone_number = request.POST.get("meeting_phone", "").strip()
            selected_date_raw = request.POST.get("meeting_date", "").strip()
            selected_timeslot = request.POST.get("meeting_timeslot", "").strip()

            schedule_data = {
                "name": name,
                "email": email,
                "phone_number": phone_number,
                "date": selected_date_raw,
                "timeslot": selected_timeslot,
            }

            allowed_slots = {slot[0] for slot in TIME_SLOT_CHOICES}
            if not all([name, email, selected_date_raw, selected_timeslot]):
                messages.error(request, "Please complete all required fields to schedule your meeting.")
                return _render_contact(request, schedule_data=schedule_data, schedule_modal_open=True)

            if selected_timeslot not in allowed_slots:
                messages.error(request, "The selected time slot is not valid.")
                return _render_contact(request, schedule_data=schedule_data, schedule_modal_open=True)

            try:
                selected_date = dt_date.fromisoformat(selected_date_raw)
            except ValueError:
                messages.error(request, "The selected date is not valid.")
                return _render_contact(request, schedule_data=schedule_data, schedule_modal_open=True)

            utc_today = timezone.now().astimezone(dt_timezone.utc).date()
            if selected_date < utc_today:
                messages.error(request, "You cannot select a past date.")
                return _render_contact(request, schedule_data=schedule_data, schedule_modal_open=True)

            if selected_date.weekday() >= 5:
                messages.error(request, "Weekend dates are not available. Please choose a weekday.")
                return _render_contact(request, schedule_data=schedule_data, schedule_modal_open=True)

            if Metting.objects.filter(date=selected_date, timeslot=selected_timeslot).exists():
                messages.error(request, "This date and time slot is already booked. Please choose another one.")
                return _render_contact(request, schedule_data=schedule_data, schedule_modal_open=True)

            Metting.objects.create(
                date=selected_date,
                name=name,
                email=email,
                phone_number=phone_number,
                timeslot=selected_timeslot,
            )
            messages.success(request, f"Your meeting has been scheduled successfully for {selected_date} at {selected_timeslot}.")
            return redirect("contact")

        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        subject = request.POST.get("subject", "").strip()
        message_text = request.POST.get("message", "").strip()

        if not all([name, email, subject, message_text]):
            messages.error(request, "Please complete all fields before sending your message.")
            return _render_contact(
                request,
                form_data={
                    "name": name,
                    "email": email,
                    "subject": subject,
                    "message": message_text,
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
        messages.success(request, f"Thanks! Your message has been sent successfully. We will reply at {email} as soon as possible.")
        return redirect("contact")

    return _render_contact(request)