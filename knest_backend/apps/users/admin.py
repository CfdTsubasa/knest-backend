from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """カスタムユーザーモデルの管理画面設定"""
    
    # リスト表示設定
    list_display = ('username', 'display_name', 'email', 'emotion_state', 'is_premium', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'is_premium', 'emotion_state', 'date_joined')
    search_fields = ('username', 'display_name', 'email', 'bio')
    ordering = ('-date_joined',)
    
    # 詳細表示設定
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('個人情報'), {'fields': ('display_name', 'email', 'bio', 'avatar_url')}),
        (_('感情状態'), {'fields': ('emotion_state',)}),
        (_('権限'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_premium', 'groups', 'user_permissions'),
        }),
        (_('重要な日付'), {'fields': ('last_login', 'date_joined', 'last_active')}),
        (_('パスワードリセット'), {'fields': ('password_reset_token', 'password_reset_token_created')}),
    )
    
    # ユーザー作成時の設定
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'display_name', 'email', 'password1', 'password2'),
        }),
    )
    
    # 読み取り専用フィールド
    readonly_fields = ('date_joined', 'last_login', 'last_active', 'password_reset_token_created')
    
    # 1ページあたりの表示件数
    list_per_page = 25
    
    def get_queryset(self, request):
        """クエリセットの最適化"""
        return super().get_queryset(request).select_related() 