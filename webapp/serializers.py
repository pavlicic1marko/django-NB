from rest_framework import serializers

from .models import AGENT_TYPE_CHOICES, News, QAndA, Thread


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ("id", "language", "title", "slug", "text", "date", "image", "created_at")
        read_only_fields = ("id", "slug", "created_at")


class QAndASerializer(serializers.ModelSerializer):
    class Meta:
        model = QAndA
        fields = ("id", "thread", "question", "answer", "created_at")
        read_only_fields = ("id", "thread", "answer", "created_at")


class ThreadSerializer(serializers.ModelSerializer):
    q_and_as = QAndASerializer(many=True, read_only=True)

    class Meta:
        model = Thread
        fields = ("id", "user", "agent_type", "is_active", "created_at", "updated_at", "q_and_as")
        read_only_fields = ("id", "user", "is_active", "created_at", "updated_at", "q_and_as")


class StartConversationSerializer(serializers.Serializer):
    agent_type = serializers.ChoiceField(choices=AGENT_TYPE_CHOICES)
    # TODO(security): Add a maximum length and total history limit before sending
    # anonymous input to the LLM or storing it in the database.
    question = serializers.CharField(allow_blank=False, trim_whitespace=True)


class QuestionSerializer(serializers.Serializer):
    # TODO(security): Add a maximum length before forwarding this public input
    # to Ollama and storing it in the database.
    question = serializers.CharField(allow_blank=False, trim_whitespace=True)