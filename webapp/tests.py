from django.test import TestCase
from django.urls import reverse

from .models import Message


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
