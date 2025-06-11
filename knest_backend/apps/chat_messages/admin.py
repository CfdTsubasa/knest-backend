from django.contrib import admin
from .models import Message

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'circle', 'message_type', 'created_at', 'is_edited', 'is_deleted')
    list_filter = ('message_type', 'is_edited', 'is_deleted', 'created_at')
    search_fields = ('content', 'sender__username', 'circle__name')
    ordering = ('-created_at',) 