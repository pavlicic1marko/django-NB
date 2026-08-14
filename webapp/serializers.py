from rest_framework import serializers

from .models import AGENT_TYPE_CHOICES, News, QAndA, Thread


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ("id", "title", "text", "date", "image", "created_at")
        read_only_fields = ("id", "created_at")


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
    question = serializers.CharField(allow_blank=False, trim_whitespace=True)


class QuestionSerializer(serializers.Serializer):
    question = serializers.CharField(allow_blank=False, trim_whitespace=True)