import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Reaction(models.Model):
    """
    リアクションモデル
    """
    REACTION_TYPES = [
        ('empathy', _('共感')),
        ('support', _('サポート')),
        ('heart', _('ハート')),
        ('hug', _('ハグ')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey(
        'chat_messages.Message',
        on_delete=models.CASCADE,
        related_name='reactions',
        verbose_name=_('メッセージ')
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reactions',
        verbose_name=_('ユーザー')
    )
    reaction_type = models.CharField(
        _('リアクションタイプ'),
        max_length=20,
        choices=REACTION_TYPES
    )
    created_at = models.DateTimeField(_('作成日時'), auto_now_add=True)

    class Meta:
        verbose_name = _('リアクション')
        verbose_name_plural = _('リアクション')
        unique_together = ('message', 'user', 'reaction_type')

    def __str__(self):
        return f"{self.user.username} - {self.reaction_type} - {self.message.id}" 