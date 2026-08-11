from django.db import models


TIME_SLOT_CHOICES = (
    ("15:00", "15:00"),
    ("15:30", "15:30"),
    ("16:00", "16:00"),
    ("16:30", "16:30"),
)


class Message(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    def __str__(self):
        return self.subject


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

    def save(self, *args, **kwargs):
        self.time_slot, _ = TimeSlot.objects.get_or_create(date=self.date, timeslot=self.timeslot)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.date} {self.timeslot}"
