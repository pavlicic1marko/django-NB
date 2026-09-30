import os
import json
from contextlib import contextmanager
from uuid import uuid4

import django
import pytest

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.test import Client

from pages.AI_Lab_page import AILabPage


@contextmanager
def allow_sync_django_queries():
    previous_value = os.environ.get("DJANGO_ALLOW_ASYNC_UNSAFE")
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
    try:
        yield
    finally:
        if previous_value is None:
            os.environ.pop("DJANGO_ALLOW_ASYNC_UNSAFE", None)
        else:
            os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = previous_value


@pytest.fixture
def authenticated_page(page):
    base_url = os.getenv("BASE_URL", "http://127.0.0.1:8000").rstrip("/")
    email = f"ai-lab-test-{uuid4().hex}@example.com"
    with allow_sync_django_queries():
        user = get_user_model().objects.create_user(
            username=email,
            email=email,
            password="Test-Password-42!",
        )
        client = Client()
        client.force_login(user)
        session_key = client.session.session_key
    page.context.add_cookies([{
        "name": settings.SESSION_COOKIE_NAME,
        "value": client.cookies[settings.SESSION_COOKIE_NAME].value,
        "url": base_url,
    }])

    yield page

    with allow_sync_django_queries():
        Session.objects.filter(session_key=session_key).delete()
        user.delete()


def mock_ai_lab_api(route):
    request = route.request
    payload = request.post_data_json

    if request.url.endswith("/end/"):
        route.fulfill(status=200, content_type="application/json", body="{}")
        return

    if request.url.endswith("/questions/"):
        response = {
            "question": payload["question"],
            "answer": "A useful follow-up response.",
        }
        route.fulfill(
            status=201,
            content_type="application/json",
            body=json.dumps(response),
        )
        return

    question = payload["question"]
    answer = "Start with a small, measurable workflow."
    qa = {"question": question, "answer": answer}
    response = {
        "thread": {
            "id": 42,
            "agent_type": payload["agent_type"],
            "is_active": True,
            "q_and_as": [qa],
        },
        "q_and_a": qa,
    }
    route.fulfill(
        status=201,
        content_type="application/json",
        body=json.dumps(response),
    )


@pytest.mark.regression
def test_ai_lab_redirects_anonymous_user_to_login(page):
    chat = AILabPage(page)
    chat.load()

    assert "/login/" in page.url
    assert page.get_by_role("heading", name="Log in").is_visible()


@pytest.mark.regression
def test_ai_lab_consultation_flow(authenticated_page):
    page = authenticated_page
    page.route("**/api/ai-lab/threads**", mock_ai_lab_api)
    chat = AILabPage(page)
    chat.load()

    assert chat.is_heading_visible()
    assert not chat.can_start_consultation()
    chat.select_agent("gemma3:270m")
    assert chat.is_agent_selected("gemma3:270m")

    chat.enter_message("How can AI help my team?")
    assert chat.can_start_consultation()
    chat.start_consultation()

    chat.wait_for_message("How can AI help my team?")
    chat.wait_for_message("Start with a small, measurable workflow.")
    assert chat.is_conversation_visible()
    assert chat.is_agent_selection_disabled()

    chat.enter_followup("What should we measure first?")
    assert chat.can_send_followup()
    chat.send_followup()
    chat.wait_for_message("What should we measure first?")
    chat.wait_for_message("A useful follow-up response.")

    chat.end_consultation()
    chat.expect_consultation_ended()