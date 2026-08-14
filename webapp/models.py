from django.conf import settings
from django.db import models


TIME_SLOT_CHOICES = (
    ("15:00", "15:00"),
    ("15:30", "15:30"),
    ("16:00", "16:00"),
    ("16:30", "16:30"),
)

AGENT_TYPE_CHOICES = (
    ("general", "General"),
    ("technical", "Technical"),
    ("sales", "Sales"),
)


class Thread(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="chat_threads",
    )
    agent_type = models.CharField(max_length=20, choices=AGENT_TYPE_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Thread {self.pk} ({self.agent_type})"


class QAndA(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name="q_and_as")
    question = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_at", "id")

    def __str__(self):
        return f"Q&A {self.pk} for Thread {self.thread_id}"


class Message(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    def __str__(self):
        return self.subject


class News(models.Model):
    title = models.CharField(max_length=200, unique=True)
    text = models.TextField()
    date = models.DateField()
    image = models.ImageField(upload_to="news/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class TimeSlot(models.Model):
    date = models.DateField()
    timeslot = models.CharField(max_length=5, choices=TIME_SLOT_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["date", "timeslot"], name="unique_date_timeslot")
        ]

    def __str__(self):
        return f"{self.date} {self.timeslot}"


class Metting(models.Model):
    date = models.DateField()
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    timeslot = models.CharField(max_length=5, choices=TIME_SLOT_CHOICES)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.PROTECT, related_name="mettings", null=True, blank=True, editable=False)
    crated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["date", "timeslot"], name="unique_metting_date_timeslot")
        ]

    def save(self, *args, **kwargs):
        self.time_slot, _ = TimeSlot.objects.get_or_create(date=self.date, timeslot=self.timeslot)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.date} {self.timeslot}"
