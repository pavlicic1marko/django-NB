from django.contrib import admin
from .models import Message, Metting, TimeSlot, News


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
	list_display = ("name", "email", "subject", "created_at")
	search_fields = ("name", "email", "subject", "message")
	list_filter = ("created_at",)
	ordering = ("-created_at",)


@admin.register(Metting)
class MettingAdmin(admin.ModelAdmin):
	list_display = ("name", "email", "phone_number", "date", "timeslot", "time_slot", "crated_at")
	search_fields = ("name", "email", "phone_number")
	list_filter = ("date", "timeslot", "crated_at")
	ordering = ("-crated_at",)


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
	list_display = ("date", "timeslot", "created_at")
	search_fields = ("date", "timeslot")
	list_filter = ("date", "timeslot", "created_at")
	ordering = ("-created_at",)

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
	list_display = ("title", "created_at")
	search_fields = ("title", "content")
	list_filter = ("created_at",)
	ordering = ("-created_at",)
