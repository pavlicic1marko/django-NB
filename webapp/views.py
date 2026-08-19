from datetime import date as dt_date
from datetime import timezone as dt_timezone
from collections import defaultdict

import requests
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.db import transaction
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response

from .models import Message, Metting, News, QAndA, Thread, TIME_SLOT_CHOICES
from .serializers import NewsSerializer, QAndASerializer, QuestionSerializer, StartConversationSerializer, ThreadSerializer

AGENT_INSTRUCTIONS = {
    "general": (
        "You are a helpful general-purpose assistant. Answer clearly and accurately. "
        "If you are unsure, say so instead of inventing information. The website includes a home "
        "page for an overview, an About Us page with company information, a Products page for "
        "offerings, a Blog page for updates, and a Contact page for messages and meeting "
        "scheduling. It also provides a Chat page where visitors can choose an assistant and ask "
        "questions. Describe these pages at a basic level and do not invent details that are not "
        "provided."
    ),
    "technical": (
        "You are a technical support assistant for an IT studio. Help users with products, "
        "integrations, software, and troubleshooting. Give practical step-by-step explanations "
        "and ask for missing technical details when necessary. This application is built with "
        "Django, using its views, models, templates, and REST APIs to provide a reliable web "
        "experience. It is deployed on AWS and uses modern web-development practices and "
        "technologies. Explain technical concepts clearly, and do not claim deployment details, "
        "services, or capabilities that have not been confirmed."
    ),
    "sales": (
        "You are a professional sales assistant for an IT studio. Answer questions about products, "
        "pricing, services, and project fit. Be helpful and informative without making up prices, "
        "guarantees, or features. The Products page provides an overview of the available "
        "offerings. When a visitor is interested in learning more, direct them to the Contact "
        "page, where they can send a message or schedule a meeting."
    ),
}


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


def chat(request):
    return render(request, "website/chat.html")


class NewsViewSet(viewsets.ModelViewSet):
    queryset = News.objects.all().order_by("-created_at")
    serializer_class = NewsSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "id"


@api_view(["POST"])
@authentication_classes([])
@permission_classes([permissions.AllowAny])
def start_conversation(request):
    serializer = StartConversationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    with transaction.atomic():
        thread = Thread.objects.create(agent_type=serializer.validated_data["agent_type"])
        question = serializer.validated_data["question"]
        q_and_a = QAndA.objects.create(
            thread=thread,
            question=question,
            answer="",
        )

        q_and_as = QAndA.objects.filter(thread=thread).order_by("created_at", "id")
        messages = [
            {
                "role": "system",
                "content": AGENT_INSTRUCTIONS[thread.agent_type],
            }
        ]
        for existing_q_and_a in q_and_as:
            messages.append({"role": "user", "content": existing_q_and_a.question})
            if existing_q_and_a.answer:
                messages.append({"role": "assistant", "content": existing_q_and_a.answer})

        try:
            response = requests.post(
                "http://localhost:11434/api/chat",
                json={
                    "model": settings.OLLAMA_MODEL,
                    "messages": messages,
                    "stream": False,
                },
                timeout=60,
            )
            response.raise_for_status()
            answer = response.json()["message"]["content"]
            if not isinstance(answer, str):
                raise ValueError("Ollama returned an invalid answer.")
        except requests.exceptions.RequestException:
            transaction.set_rollback(True)
            return Response(
                {"detail": "There was an error. Please try again later."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except (KeyError, TypeError, ValueError):
            transaction.set_rollback(True)
            return Response(
                {"detail": "Ollama returned an invalid response."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        q_and_a.answer = answer
        q_and_a.save(update_fields=["answer"])

    return Response(
        {"thread": ThreadSerializer(thread).data, "q_and_a": QAndASerializer(q_and_a).data},
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
@authentication_classes([])
@permission_classes([permissions.AllowAny])
def get_conversation(request, thread_id):
    thread = get_object_or_404(Thread.objects.prefetch_related("q_and_as"), pk=thread_id)
    return Response(ThreadSerializer(thread).data)


@api_view(["POST"])
@authentication_classes([])
@permission_classes([permissions.AllowAny])
def add_question(request, thread_id):
    thread = get_object_or_404(Thread, pk=thread_id)
    serializer = QuestionSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    if not thread.is_active:
        return Response({"detail": "This conversation has ended."}, status=status.HTTP_400_BAD_REQUEST)

    question = serializer.validated_data["question"]
    q_and_a = QAndA.objects.create(
        thread=thread,
        question=question,
        answer="",
    )
    q_and_as = QAndA.objects.filter(thread=thread).order_by("created_at", "id")
    messages = [
        {
            "role": "system",
            "content": AGENT_INSTRUCTIONS[thread.agent_type],
        }
    ]
    for existing_q_and_a in q_and_as:
        messages.append({"role": "user", "content": existing_q_and_a.question})
        if existing_q_and_a.answer:
            messages.append({"role": "assistant", "content": existing_q_and_a.answer})

    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": settings.OLLAMA_MODEL,
                "messages": messages,
                "stream": False,
            },
            timeout=60,
        )
        response.raise_for_status()
        answer = response.json()["message"]["content"]
        if not isinstance(answer, str):
            raise ValueError("Ollama returned an invalid answer.")
    except requests.exceptions.RequestException:
        q_and_a.delete()
        return Response(
            {"detail": "There was an error. Please try again later."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    except (KeyError, TypeError, ValueError):
        q_and_a.delete()
        return Response(
            {"detail": "Ollama returned an invalid response."},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    q_and_a.answer = answer
    q_and_a.save(update_fields=["answer"])
    return Response(QAndASerializer(q_and_a).data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@authentication_classes([])
@permission_classes([permissions.AllowAny])
def end_conversation(request, thread_id):
    thread = get_object_or_404(Thread, pk=thread_id)
    if thread.is_active:
        thread.is_active = False
        thread.save(update_fields=["is_active", "updated_at"])
    return Response(ThreadSerializer(thread).data)


def blog(request):
    article_page = Paginator(News.objects.order_by("-date", "-id"), 10).get_page(request.GET.get("page"))
    return render(request, "website/blog.html", {"article_page": article_page})


def news_detail(request, news_id):
    article = get_object_or_404(News, pk=news_id)
    suggested_articles = News.objects.none()
    if News.objects.count() >= 2:
        suggested_articles = News.objects.exclude(pk=article.pk).order_by("-date", "-id")[:2]
    return render(
        request,
        "website/news_detail.html",
        {"article": article, "suggested_articles": suggested_articles},
    )


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