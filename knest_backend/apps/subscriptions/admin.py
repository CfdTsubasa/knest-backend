from django.contrib import admin
from .models import Subscription

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'status', 'start_date', 'end_date', 'auto_renew')
    list_filter = ('plan', 'status', 'auto_renew')
    search_fields = ('user__username',)
    ordering = ('-created_at',) 