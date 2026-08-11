from django.db import models


class Message(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    def __str__(self):
        return self.subject


class Metting(models.Model):
    class TimeSlot(models.TextChoices):
        SLOT_1500 = "15:00", "15:00"
        SLOT_1530 = "15:30", "15:30"
        SLOT_1600 = "16:00", "16:00"
        SLOT_1630 = "16:30", "16:30"

    date = models.DateField()
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    timeslot = models.CharField(max_length=5, choices=TimeSlot.choices)
    crated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.date} {self.timeslot}"
