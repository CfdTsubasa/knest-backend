import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Message(models.Model):
    """
    メッセージモデル
    """
    MESSAGE_TYPES = [
        ('text', _('テキスト')),
        ('emotion', _('感情')),
        ('support_request', _('サポート要請')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    circle = models.ForeignKey(
        'circles.Circle',
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name=_('サークル')
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        verbose_name=_('送信者')
    )
    content = models.TextField(_('内容'))
    message_type = models.CharField(
        _('メッセージタイプ'),
        max_length=20,
        choices=MESSAGE_TYPES,
        default='text'
    )
    emotion_tag = models.CharField(_('感情タグ'), max_length=50, blank=True, null=True)
    reply_to = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name=_('返信先')
    )
    created_at = models.DateTimeField(_('作成日時'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新日時'), auto_now=True)
    is_edited = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('メッセージ')
        verbose_name_plural = _('メッセージ')
        ordering = ['-created_at']
        db_table = 'messages'

    def __str__(self):
        return f"{self.sender.username} - {self.circle.name} ({self.created_at.strftime('%Y-%m-%d %H:%M')})" 