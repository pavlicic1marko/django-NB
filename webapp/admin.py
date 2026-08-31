from django.contrib import admin
from .models import Message, Metting, News, QAndA, Thread, TimeSlot


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
	list_display = ("title", "language", "created_at")
	search_fields = ("title", "content")
	list_filter = ("language", "created_at")
	ordering = ("-created_at",)


@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
	list_display = ("id", "user", "agent_type", "is_active", "created_at", "updated_at")
	list_filter = ("agent_type", "is_active", "created_at")
	ordering = ("-created_at",)


@admin.register(QAndA)
class QAndAAdmin(admin.ModelAdmin):
	list_display = ("id", "thread", "question", "created_at")
	search_fields = ("question", "answer")
	ordering = ("-created_at",)
