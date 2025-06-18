from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Circle, CircleMembership, CirclePost, CircleEvent, CircleChat, CircleSearchHistory, CircleChatRead

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)

@admin.register(Circle)
class CircleAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'circle_type', 'member_count', 'owner', 'created_at')
    list_filter = ('status', 'circle_type', 'is_premium', 'created_at')
    search_fields = ('name', 'description', 'owner__username')
    readonly_fields = ('id', 'member_count', 'post_count', 'last_activity', 'created_at', 'updated_at')
    filter_horizontal = ('categories', 'interests')
    
    fieldsets = (
        ('基本情報', {
            'fields': ('id', 'name', 'description', 'owner', 'creator')
        }),
        ('設定', {
            'fields': ('status', 'circle_type', 'is_premium', 'member_limit', 'is_private')
        }),
        ('カテゴリー・興味', {
            'fields': ('categories', 'interests', 'tags')
        }),
        ('画像', {
            'fields': ('icon_url', 'cover_url')
        }),
        ('統計情報', {
            'fields': ('member_count', 'post_count', 'last_activity'),
            'classes': ('collapse',)
        }),
        ('規約', {
            'fields': ('rules',),
            'classes': ('collapse',)
        }),
        ('タイムスタンプ', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('owner', 'creator')

@admin.register(CircleMembership)
class CircleMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'circle', 'status', 'role', 'joined_at')
    list_filter = ('status', 'role', 'joined_at')
    search_fields = ('user__username', 'user__email', 'circle__name')
    readonly_fields = ('id', 'joined_at')
    
    fieldsets = (
        ('基本情報', {
            'fields': ('id', 'user', 'circle')
        }),
        ('メンバーシップ', {
            'fields': ('status', 'role', 'joined_at')
        }),
        ('申請・拒否', {
            'fields': ('application_message', 'rejection_reason'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'circle')

@admin.register(CirclePost)
class CirclePostAdmin(admin.ModelAdmin):
    list_display = ('circle', 'author', 'content_preview', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('circle__name', 'author__username', 'content')
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'コンテンツプレビュー'

@admin.register(CircleEvent)
class CircleEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'circle', 'start_datetime', 'end_datetime', 'location')
    list_filter = ('start_datetime', 'created_at')
    search_fields = ('title', 'circle__name', 'description', 'location')
    readonly_fields = ('id', 'created_at', 'updated_at')

@admin.register(CircleChat)
class CircleChatAdmin(admin.ModelAdmin):
    list_display = ('circle', 'sender', 'content_preview', 'created_at', 'is_system_message')
    list_filter = ('created_at', 'is_edited', 'is_system_message')
    search_fields = ('circle__name', 'sender__username', 'content')
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'メッセージプレビュー'

@admin.register(CircleSearchHistory)
class CircleSearchHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'search_query', 'results_count', 'searched_at')
    list_filter = ('searched_at',)
    search_fields = ('user__username', 'search_query')
    readonly_fields = ('id', 'searched_at')

@admin.register(CircleChatRead)
class CircleChatReadAdmin(admin.ModelAdmin):
    list_display = ('user', 'circle', 'last_read')
    list_filter = ('last_read',)
    search_fields = ('user__username', 'circle__name')
    readonly_fields = ('id', 'last_read') 