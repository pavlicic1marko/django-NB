from datetime import date as dt_date
from datetime import timezone as dt_timezone
from collections import defaultdict
import logging

import requests
from django.contrib import messages
from django.core.cache import cache
from django.core.paginator import Paginator
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import get_language, gettext as _
from django.urls import translate_url
from django.db import transaction
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response

from .models import Message, Metting, News, QAndA, Thread, TIME_SLOT_CHOICES
from .serializers import NewsSerializer, QAndASerializer, QuestionSerializer, StartConversationSerializer, ThreadSerializer

logger = logging.getLogger('webapp')

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

GERMAN_AGENT_INSTRUCTIONS = {
    "general": (
        "Du bist ein hilfreicher allgemeiner Assistent. Antworte klar und korrekt auf Deutsch. "
        "Wenn du dir unsicher bist, sage das, statt Informationen zu erfinden. Die Website bietet "
        "eine Startseite, eine Uber-uns-Seite, eine Produktseite, einen Blog, eine Kontaktseite und "
        "einen Chat. Beschreibe diese Seiten nur auf Grundlage der vorhandenen Informationen."
    ),
    "technical": (
        "Du bist ein technischer Support-Assistent fur ein IT-Studio. Hilf bei Produkten, "
        "Integrationen, Software und Fehlerbehebung mit praktischen Schritt-fur-Schritt-Erklarungen. "
        "Diese Anwendung basiert auf Django und wird auf AWS bereitgestellt. Erfinde keine nicht "
        "bestatigten Bereitstellungsdetails, Dienste oder Funktionen."
    ),
    "sales": (
        "Du bist ein professioneller Vertriebsassistent fur ein IT-Studio. Beantworte Fragen zu "
        "Produkten, Preisen, Dienstleistungen und Projektpassung auf Deutsch. Erfinde keine Preise, "
        "Garantien oder Funktionen. Verweise Interessierte fur weitere Informationen auf die Kontaktseite."
    ),
}

CONTACT_RATE_LIMITS = {
    "message": (3, 60 * 60),
    "schedule": (2, 60 * 60),
}


def _client_ip(request):
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    return forwarded_for.split(",")[0].strip() if forwarded_for else request.META.get("REMOTE_ADDR", "unknown")


def _agent_instruction(agent_type):
    instructions = GERMAN_AGENT_INSTRUCTIONS if get_language() == "de" else AGENT_INSTRUCTIONS
    return instructions[agent_type]


def switch_language(request, language):
    if language not in dict(settings.LANGUAGES):
        return redirect("home")

    next_url = request.GET.get("next", "")
    if not url_has_allowed_host_and_scheme(next_url, {request.get_host()}, request.is_secure()):
        next_url = "/"

    response = redirect(translate_url(next_url, language))
    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language)
    return response


def _rate_limit_exceeded(request, action):
    limit, window = CONTACT_RATE_LIMITS[action]
    cache_key = f"contact-rate:{action}:{_client_ip(request)}"
    if cache.add(cache_key, 1, timeout=window):
        return False
    try:
        attempts = cache.incr(cache_key)
    except ValueError:
        cache.set(cache_key, 1, timeout=window)
        return False
    return attempts > limit


def _future_booked_slots_by_date():
    utc_today = timezone.now().astimezone(dt_timezone.utc).date()
    slot_order = [slot_value for slot_value, _ in TIME_SLOT_CHOICES]
    slots = defaultdict(set)
    slots[utc_today.isoformat()].update(slot_order)

    for slot_date, slot_time in Metting.objects.filter(date__gt=utc_today).values_list("date", "timeslot"):
        slots[slot_date.isoformat()].add(slot_time)

    return {date_key: [slot for slot in slot_order if slot in slot_values] for date_key, slot_values in slots.items()}


def _render_contact(request, form_data=None, schedule_data=None, schedule_modal_open=False, status=200):
    return render(
        request,
        "website/contact.html",
        {
            "form_data": form_data or {},
            "schedule_data": schedule_data or {},
            "schedule_modal_open": schedule_modal_open,
            "booked_slots_by_date": _future_booked_slots_by_date(),
        },
        status=status,
    )


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
    # TODO(security): Use ReadOnlyModelViewSet for public access and require an
    # authenticated staff user for create, update, and delete operations.
    permission_classes = [permissions.AllowAny]
    lookup_field = "id"


@api_view(["POST"])
@authentication_classes([])
@permission_classes([permissions.AllowAny])
def start_conversation(request):
    # TODO(security): Rate-limit anonymous callers and bind each thread to a
    # session or authenticated user to prevent abuse and cross-user disclosure.
    serializer = StartConversationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    with transaction.atomic():
        thread = Thread.objects.create(agent_type=serializer.validated_data["agent_type"])
        logger.info("New chatbot conversation started: thread_id=%s agent_type=%s", thread.id, thread.agent_type)
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
                "content": _agent_instruction(thread.agent_type),
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
            logger.exception(
                "Chat request failed: thread_id=%s agent_type=%s",
                thread.id,
                thread.agent_type,
            )
            transaction.set_rollback(True)
            return Response(
                {"detail": _("There was an error. Please try again later.")},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except (KeyError, TypeError, ValueError):
            logger.exception(
                "Chat response was invalid: thread_id=%s agent_type=%s",
                thread.id,
                thread.agent_type,
            )
            transaction.set_rollback(True)
            return Response(
                {"detail": _("Ollama returned an invalid response.")},
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
    # TODO(security): Do not look up conversations by public sequential ID alone;
    # verify ownership before returning the thread and its private history.
    thread = get_object_or_404(Thread.objects.prefetch_related("q_and_as"), pk=thread_id)
    return Response(ThreadSerializer(thread).data)


@api_view(["POST"])
@authentication_classes([])
@permission_classes([permissions.AllowAny])
def add_question(request, thread_id):
    # TODO(security): Enforce thread ownership, cap question/history size, and
    # rate-limit requests before invoking the local LLM service.
    thread = get_object_or_404(Thread, pk=thread_id)
    serializer = QuestionSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    if not thread.is_active:
        return Response({"detail": _("This conversation has ended.")}, status=status.HTTP_400_BAD_REQUEST)

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
            "content": _agent_instruction(thread.agent_type),
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
        logger.exception(
            "Chat request failed: thread_id=%s agent_type=%s",
            thread.id,
            thread.agent_type,
        )
        q_and_a.delete()
        return Response(
            {"detail": _("There was an error. Please try again later.")},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    except (KeyError, TypeError, ValueError):
        logger.exception(
            "Chat response was invalid: thread_id=%s agent_type=%s",
            thread.id,
            thread.agent_type,
        )
        q_and_a.delete()
        return Response(
            {"detail": _("Ollama returned an invalid response.")},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    q_and_a.answer = answer
    q_and_a.save(update_fields=["answer"])
    return Response(QAndASerializer(q_and_a).data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@authentication_classes([])
@permission_classes([permissions.AllowAny])
def end_conversation(request, thread_id):
    # TODO(security): Require the thread owner or an authenticated staff user
    # before allowing an anonymous caller to end a conversation.
    thread = get_object_or_404(Thread, pk=thread_id)
    if thread.is_active:
        thread.is_active = False
        thread.save(update_fields=["is_active", "updated_at"])
    return Response(ThreadSerializer(thread).data)


def blog(request):
    articles = News.objects.filter(language=get_language()).order_by("-date", "-id")
    article_page = Paginator(articles, 10).get_page(request.GET.get("page"))
    return render(request, "website/blog.html", {"article_page": article_page})


def news_detail(request, slug):
    articles = News.objects.filter(language=get_language())
    article = get_object_or_404(articles, slug=slug)
    suggested_articles = News.objects.none()
    if articles.count() >= 2:
        suggested_articles = articles.exclude(pk=article.pk).order_by("-date", "-id")[:2]
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

            if _rate_limit_exceeded(request, "schedule"):
                messages.warning(request, _("Too many booking attempts. Please try again later."))
                return _render_contact(
                    request,
                    schedule_data=schedule_data,
                    schedule_modal_open=True,
                    status=429,
                )

            allowed_slots = {slot[0] for slot in TIME_SLOT_CHOICES}
            if not all([name, email, selected_date_raw, selected_timeslot]):
                messages.error(request, _("Please complete all required fields to schedule your meeting."))
                return _render_contact(request, schedule_data=schedule_data, schedule_modal_open=True)

            if selected_timeslot not in allowed_slots:
                messages.error(request, _("The selected time slot is not valid."))
                return _render_contact(request, schedule_data=schedule_data, schedule_modal_open=True)

            try:
                selected_date = dt_date.fromisoformat(selected_date_raw)
            except ValueError:
                messages.error(request, _("The selected date is not valid."))
                return _render_contact(request, schedule_data=schedule_data, schedule_modal_open=True)

            utc_today = timezone.now().astimezone(dt_timezone.utc).date()
            if selected_date < utc_today:
                messages.error(request, _("You cannot select a past date."))
                return _render_contact(request, schedule_data=schedule_data, schedule_modal_open=True)

            if selected_date.weekday() >= 5:
                messages.error(request, _("Weekend dates are not available. Please choose a weekday."))
                return _render_contact(request, schedule_data=schedule_data, schedule_modal_open=True)

            if Metting.objects.filter(date=selected_date, timeslot=selected_timeslot).exists():
                messages.error(request, _("This date and time slot is already booked. Please choose another one."))
                return _render_contact(request, schedule_data=schedule_data, schedule_modal_open=True)

            try:
                Metting.objects.create(
                    date=selected_date,
                    name=name,
                    email=email,
                    phone_number=phone_number,
                    timeslot=selected_timeslot,
                )
            except Exception:
                logger.exception("Meeting scheduling failed")
                messages.error(request, _("We could not schedule your meeting. Please try again later."))
                return _render_contact(request, schedule_data=schedule_data, schedule_modal_open=True, status=500)
            messages.success(
                request,
                _("Your meeting has been scheduled successfully for %(date)s at %(time)s.")
                % {"date": selected_date, "time": selected_timeslot},
            )
            return redirect("contact")

        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        subject = request.POST.get("subject", "").strip()
        message_text = request.POST.get("message", "").strip()

        if _rate_limit_exceeded(request, "message"):
            messages.warning(request, _("Too many messages have been sent. Please try again later."))
            return _render_contact(
                request,
                form_data={
                    "name": name,
                    "email": email,
                    "subject": subject,
                    "message": message_text,
                },
                status=429,
            )

        if not all([name, email, subject, message_text]):
            messages.error(request, _("Please complete all fields before sending your message."))
            return _render_contact(
                request,
                form_data={
                    "name": name,
                    "email": email,
                    "subject": subject,
                    "message": message_text,
                },
            )

        try:
            Message.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message_text,
                ip_address=_client_ip(request),
            )
        except Exception:
            logger.exception("Contact message could not be saved")
            messages.error(request, _("We could not send your message. Please try again later."))
            return _render_contact(
                request,
                form_data={
                    "name": name,
                    "email": email,
                    "subject": subject,
                    "message": message_text,
                },
                status=500,
            )
        messages.success(
            request,
            _("Thanks! Your message has been sent successfully. We will reply at %(email)s as soon as possible.")
            % {"email": email},
        )
        return redirect("contact")

    return _render_contact(request)