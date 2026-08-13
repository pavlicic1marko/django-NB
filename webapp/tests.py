import base64
from datetime import date

from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse

from .models import Message, News
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


class NewsViewTests(TestCase):
    def test_first_page_shows_ten_articles_and_pagination(self):
        response = self.client.get(reverse("news"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["article_page"].object_list), 10)
        self.assertContains(response, "Operations briefing: August service update")
        self.assertNotContains(response, "Community update: June milestones")

    def test_second_page_shows_remaining_articles(self):
        response = self.client.get(reverse("news"), {"page": 2})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["article_page"].object_list), 2)
        self.assertContains(response, "Community update: June milestones")


class NewsApiTests(TestCase):
    def test_news_api_supports_crud_operations(self):
        image = SimpleUploadedFile(
            "news.png",
            base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAF" "c0N0AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJ0UkG" "AAAAAQMEBQAAAAAABQAAEEpQwAAAABJRU5ErkJggg=="),
            content_type="image/png",
        )

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
    def test_title_must_be_unique_and_created_at_is_set_automatically(self):
        article = News.objects.create(
            title="Weekly operations update",
            text="The latest operational information.",
            date=date(2026, 8, 12),
            image="news/update.png",
        )

        self.assertIsNotNone(article.created_at)
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
            {"id", "title", "text", "date", "image", "created_at"},
        )
        self.assertTrue(serializer.fields["id"].read_only)
        self.assertTrue(serializer.fields["created_at"].read_only)
