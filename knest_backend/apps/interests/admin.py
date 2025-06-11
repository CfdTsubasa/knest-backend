from django.contrib import admin
from .models import Interest, UserInterest, Tag, UserTag

@admin.register(Interest)
class InterestAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_official', 'usage_count', 'created_at')
    list_filter = ('category', 'is_official')
    search_fields = ('name', 'description')
    ordering = ('-usage_count', 'name')

@admin.register(UserInterest)
class UserInterestAdmin(admin.ModelAdmin):
    """ユーザー興味関心の管理画面（シンプル版）"""
    list_display = ('user', 'interest', 'added_at')
    list_filter = ('interest__category', 'added_at')
    search_fields = ('user__username', 'interest__name')
    raw_id_fields = ('user', 'interest')
    ordering = ('-added_at',)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'usage_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name',)
    readonly_fields = ('created_at',)
    ordering = ('-usage_count', 'name')

@admin.register(UserTag)
class UserTagAdmin(admin.ModelAdmin):
    list_display = ('user', 'tag', 'added_at')
    list_filter = ('added_at', 'tag')
    search_fields = ('user__username', 'tag__name')
    readonly_fields = ('added_at',)
    ordering = ('-added_at',) 