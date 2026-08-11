from django.test import TestCase

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
