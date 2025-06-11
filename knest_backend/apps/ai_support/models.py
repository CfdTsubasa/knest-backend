import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

class AISupportSession(models.Model):
    """
    AIサポートセッションモデル
    """
    SESSION_STATUS_CHOICES = [
        ('active', '進行中'),
        ('completed', '完了'),
        ('cancelled', 'キャンセル'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ai_support_sessions',
        verbose_name=_('ユーザー')
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=SESSION_STATUS_CHOICES, default='active')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_interaction_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('AIサポートセッション')
        verbose_name_plural = _('AIサポートセッション')
        ordering = ['-last_interaction_at']
        db_table = 'ai_support_sessions'

    def __str__(self):
        return f"{self.user.username} - {self.title}"

class AISupportMessage(models.Model):
    """
    AIサポートメッセージモデル
    """
    MESSAGE_TYPES = [
        ('user', _('ユーザー')),
        ('ai', _('AI')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        AISupportSession,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name=_('セッション')
    )
    message_type = models.CharField(
        _('メッセージタイプ'),
        max_length=10,
        choices=MESSAGE_TYPES
    )
    content = models.TextField(_('内容'))
    created_at = models.DateTimeField(_('作成日時'), auto_now_add=True)

    class Meta:
        verbose_name = _('AIサポートメッセージ')
        verbose_name_plural = _('AIサポートメッセージ')
        ordering = ['created_at']

    def __str__(self):
        return f"{self.session.id} - {self.message_type} ({self.created_at.strftime('%H:%M:%S')})" 