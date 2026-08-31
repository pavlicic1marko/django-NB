from io import BytesIO
from datetime import date

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from django.db import DatabaseError, IntegrityError
from django.test import TestCase
from django.urls import reverse
from django.utils import translation
from PIL import Image
from unittest.mock import patch

from .models import Message, Metting, News, QAndA, Thread
from .serializers import NewsSerializer


class MessageModelTests(TestCase):
    def test_message_can_be_created_with_user_fields(self):
        message = Message.objects.create(
            name="Alice",
            email="alice@example.com",
            subject="Hello",
            message="This is a test message",
            ip_address="203.0.113.10",
        )

        self.assertEqual(message.name, "Alice")
        self.assertEqual(message.email, "alice@example.com")
        self.assertEqual(message.subject, "Hello")
        self.assertEqual(message.message, "This is a test message")
        self.assertEqual(message.ip_address, "203.0.113.10")
        self.assertIsNotNone(message.created_at)


class ContactRateLimitTests(TestCase):
    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    def test_project_brief_rate_limit_is_enforced_server_side(self):
        payload = {
            "name": "Alice",
            "email": "alice@example.com",
            "subject": "Project brief",
            "message": "Please help with an AI project.",
        }

        for _ in range(3):
            response = self.client.post(reverse("contact"), payload)
            self.assertEqual(response.status_code, 302)

        response = self.client.post(reverse("contact"), payload)

        self.assertEqual(response.status_code, 429)
        self.assertEqual(Message.objects.count(), 3)

    def test_booking_rate_limit_is_enforced_server_side(self):
        payload = {
            "form_type": "schedule",
            "meeting_name": "Alice",
            "meeting_email": "alice@example.com",
            "meeting_date": "2026-09-01",
            "meeting_timeslot": "15:00",
        }

        for index in range(2):
            response = self.client.post(reverse("schedule_meeting"), payload)
            self.assertEqual(response.status_code, 302 if index == 0 else 200)

        response = self.client.post(reverse("schedule_meeting"), payload)

        self.assertEqual(response.status_code, 429)


class ContactFailureLoggingTests(TestCase):
    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    @patch("webapp.views.Message.objects.create", side_effect=DatabaseError("database unavailable"))
    def test_message_save_failure_is_logged_and_shown_to_visitor(self, create_message):
        with self.assertLogs("webapp", level="ERROR") as captured_logs:
            response = self.client.post(
                reverse("contact"),
                {
                    "name": "Alice",
                    "email": "alice@example.com",
                    "subject": "Project brief",
                    "message": "Please help with an AI project.",
                },
            )

        self.assertEqual(response.status_code, 500)
        self.assertContains(response, "We could not send your message.", status_code=500)
        self.assertEqual(Message.objects.count(), 0)
        self.assertTrue(any("Contact message could not be saved" in entry for entry in captured_logs.output))

    @patch("webapp.views.Metting.objects.create", side_effect=DatabaseError("database unavailable"))
    def test_meeting_schedule_failure_is_logged_and_shown_to_visitor(self, create_meeting):
        with self.assertLogs("webapp", level="ERROR") as captured_logs:
            response = self.client.post(
                reverse("schedule_meeting"),
                {
                    "form_type": "schedule",
                    "meeting_name": "Alice",
                    "meeting_email": "alice@example.com",
                    "meeting_date": "2026-09-01",
                    "meeting_timeslot": "15:00",
                },
            )

        self.assertEqual(response.status_code, 500)
        self.assertContains(response, "We could not schedule your meeting.", status_code=500)
        self.assertEqual(Metting.objects.count(), 0)
        self.assertTrue(any("Meeting scheduling failed" in entry for entry in captured_logs.output))


class LocaleRoutingTests(TestCase):
    def test_meta_description_is_rendered_only_on_the_home_page(self):
        home_response = self.client.get(reverse("home"))
        about_response = self.client.get(reverse("about_us"))

        self.assertContains(
            home_response,
            '<meta name="description" content="AI development, workflow automation, and software integrations built for practical business use.">',
            html=False,
        )
        self.assertNotContains(about_response, '<meta name="description"', html=False)

    def test_responses_are_excluded_from_search_indexing(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response["X-Robots-Tag"], "noindex, nofollow, noarchive")
        self.assertContains(response, '<meta name="robots" content="noindex, nofollow, noarchive">', html=False)

    def test_robots_file_disallows_every_path(self):
        response = self.client.get("/robots.txt")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/plain")
        self.assertContains(response, "User-agent: *\nDisallow: /\n", html=False)

    def test_public_pages_use_locale_prefixes_and_render_the_selected_language(self):
        response = self.client.get("/de/contact/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<html lang="de">', html=False)
        self.assertContains(response, "Kontakt")
        self.assertContains(response, 'hreflang="en"')
        self.assertContains(response, 'hreflang="de"')

    def test_language_switcher_preserves_the_current_localized_page(self):
        response = self.client.get("/language/de/?next=/en/contact/")

        self.assertRedirects(response, "/de/contact/", fetch_redirect_response=False)
        self.assertEqual(response.cookies["django_language"].value, "de")

    def test_api_urls_remain_unprefixed(self):
        response = self.client.get("/api/news/")

        self.assertEqual(response.status_code, 200)


class NewsViewTests(TestCase):
    def setUp(self):
        for index in range(12):
            News.objects.create(
                title=f"Studio update {index}",
                text=f"News text {index}",
                date=date(2026, 8, 12 - index),
                image=f"news/update-{index}.png",
            )

    def test_first_page_shows_ten_articles_and_pagination(self):
        response = self.client.get(reverse("news"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["article_page"].object_list), 10)
        self.assertContains(response, "Studio update 0")
        self.assertNotContains(response, "Studio update 10")

    def test_second_page_shows_remaining_articles(self):
        response = self.client.get(reverse("news"), {"page": 2})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["article_page"].object_list), 2)
        self.assertContains(response, "Studio update 10")

    def test_german_blog_shows_only_german_articles(self):
        News.objects.create(
            language="de",
            title="Deutsches Studio-Update",
            text="Deutsche Neuigkeiten.",
            date=date(2026, 8, 13),
            image="news/update-de.png",
        )

        with translation.override("de"):
            response = self.client.get(reverse("news"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Deutsches Studio-Update")
        self.assertNotContains(response, "Studio update 0")

    def test_news_detail_displays_the_selected_article_text(self):
        article = News.objects.get(title="Studio update 0")

        response = self.client.get(reverse("news_detail", args=[article.slug]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, article.title)
        self.assertContains(response, article.text)
        self.assertContains(response, article.image.url)
        self.assertEqual(len(response.context["suggested_articles"]), 2)
        self.assertNotIn(article, response.context["suggested_articles"])

    def test_news_detail_shows_a_suggestion_when_two_articles_exist(self):
        News.objects.exclude(title__in=["Studio update 0", "Studio update 1"]).delete()
        article = News.objects.get(title="Studio update 0")

        response = self.client.get(reverse("news_detail", args=[article.slug]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["suggested_articles"]), 1)
        self.assertContains(response, "Studio update 1")


class NewsApiTests(TestCase):
    def test_news_api_supports_crud_operations(self):
        image_buffer = BytesIO()
        Image.new("RGB", (1, 1), color="white").save(image_buffer, format="PNG")
        image = SimpleUploadedFile("news.png", image_buffer.getvalue(), content_type="image/png")

        create_response = self.client.post(
            "/api/news/",
            {
                "title": "API launch update",
                "text": "The new API is live.",
                "date": "2026-08-13",
                "image": image,
            },
            format="multipart",
        )

        self.assertEqual(create_response.status_code, 201)
        created_id = create_response.json()["id"]

        list_response = self.client.get("/api/news/")
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(list_response.json()[0]["title"], "API launch update")

        detail_response = self.client.get(f"/api/news/{created_id}/")
        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(detail_response.json()["title"], "API launch update")

        patch_response = self.client.patch(
            f"/api/news/{created_id}/",
            {"text": "The API has been updated."},
            content_type="application/json",
        )
        self.assertEqual(patch_response.status_code, 200)
        self.assertEqual(patch_response.json()["text"], "The API has been updated.")

        put_response = self.client.put(
            f"/api/news/{created_id}/",
            {
                "title": "API launch update",
                "text": "The full update has been saved.",
                "date": "2026-08-14",
                "image": image,
            },
            format="multipart",
        )
        self.assertEqual(put_response.status_code, 200)
        self.assertEqual(put_response.json()["text"], "The full update has been saved.")

        delete_response = self.client.delete(f"/api/news/{created_id}/")
        self.assertEqual(delete_response.status_code, 204)

        self.assertFalse(News.objects.filter(id=created_id).exists())


class NewsModelAndSerializerTests(TestCase):
    def test_slug_is_generated_when_a_news_article_is_created(self):
        article = News.objects.create(
            title="AI workflow launch",
            text="The latest operational information.",
            date=date(2026, 8, 12),
            image="news/update.png",
        )

        self.assertEqual(article.slug, "ai-workflow-launch")

    def test_title_must_be_unique_within_a_language_and_created_at_is_set_automatically(self):
        article = News.objects.create(
            title="Weekly operations update",
            text="The latest operational information.",
            date=date(2026, 8, 12),
            image="news/update.png",
        )

        self.assertIsNotNone(article.created_at)
        german_article = News.objects.create(
            language="de",
            title="Weekly operations update",
            text="Die neuesten Betriebsinformationen.",
            date=date(2026, 8, 13),
            image="news/update-de.png",
        )
        self.assertEqual(german_article.language, "de")
        with self.assertRaises(IntegrityError):
            News.objects.create(
                title="Weekly operations update",
                text="Duplicate title.",
                date=date(2026, 8, 13),
                image="news/duplicate.png",
            )

    def test_serializer_includes_news_fields_and_keeps_created_fields_read_only(self):
        article = News.objects.create(
            title="Platform status update",
            text="All services are operational.",
            date=date(2026, 8, 12),
            image="news/status.png",
        )

        serializer = NewsSerializer(article)

        self.assertEqual(
            set(serializer.data),
            {"id", "language", "title", "slug", "text", "date", "image", "created_at"},
        )
        self.assertTrue(serializer.fields["id"].read_only)
        self.assertTrue(serializer.fields["created_at"].read_only)


class ChatApiTests(TestCase):
    def test_start_conversation_creates_thread_and_first_q_and_a(self):
        response = self.client.post(
            "/api/chat/threads/",
            {"agent_type": "technical", "question": "How do I connect?"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Thread.objects.count(), 1)
        self.assertEqual(QAndA.objects.count(), 1)
        self.assertEqual(response.json()["thread"]["agent_type"], "technical")
        self.assertEqual(response.json()["q_and_a"]["answer"], "IDK")

    def test_follow_up_keeps_same_thread_and_returns_answer(self):
        thread = Thread.objects.create(agent_type="general")

        response = self.client.post(
            f"/api/chat/threads/{thread.pk}/questions/",
            {"question": "What next?"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["thread"], thread.pk)
        self.assertEqual(QAndA.objects.filter(thread=thread).count(), 1)
        self.assertEqual(response.json()["answer"], "IDK")

    def test_get_history_and_end_conversation_preserve_data(self):
        thread = Thread.objects.create(agent_type="sales")
        QAndA.objects.create(thread=thread, question="Question", answer="IDK")

        history_response = self.client.get(f"/api/chat/threads/{thread.pk}/")
        self.assertEqual(history_response.status_code, 200)
        self.assertEqual(len(history_response.json()["q_and_as"]), 1)

        end_response = self.client.post(f"/api/chat/threads/{thread.pk}/end/")
        self.assertEqual(end_response.status_code, 200)
        self.assertFalse(end_response.json()["is_active"])
        self.assertTrue(QAndA.objects.filter(thread=thread).exists())

    def test_follow_up_cannot_be_added_after_thread_ends(self):
        thread = Thread.objects.create(agent_type="general", is_active=False)

        response = self.client.post(
            f"/api/chat/threads/{thread.pk}/questions/",
            {"question": "Still there?"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(QAndA.objects.count(), 0)
