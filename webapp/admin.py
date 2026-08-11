from django.contrib import admin
from .models import Message, Metting


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
	list_display = ("name", "email", "subject", "created_at")
	search_fields = ("name", "email", "subject", "message")
	list_filter = ("created_at",)
	ordering = ("-created_at",)


@admin.register(Metting)
class MettingAdmin(admin.ModelAdmin):
	list_display = ("name", "email", "phone_number", "date", "timeslot", "crated_at")
	search_fields = ("name", "email", "phone_number")
	list_filter = ("date", "timeslot", "crated_at")
	ordering = ("-crated_at",)
