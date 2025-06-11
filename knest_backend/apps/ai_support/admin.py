from django.contrib import admin
from .models import AISupportSession, AISupportMessage

@admin.register(AISupportSession)
class AISupportSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'status', 'started_at', 'completed_at', 'last_interaction_at')
    list_filter = ('status', 'started_at', 'completed_at')
    search_fields = ('title', 'description', 'user__username')
    readonly_fields = ('started_at', 'completed_at', 'last_interaction_at')
    ordering = ('-last_interaction_at',)

@admin.register(AISupportMessage)
class AISupportMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'message_type', 'created_at')
    list_filter = ('message_type', 'created_at')
    search_fields = ('content', 'session__title')
    readonly_fields = ('created_at',)
    ordering = ('created_at',) 