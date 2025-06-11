import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Subscription(models.Model):
    """
    サブスクリプションモデル
    """
    PLAN_CHOICES = [
        ('free', '無料プラン'),
        ('basic', 'ベーシックプラン'),
        ('premium', 'プレミアムプラン'),
    ]

    STATUS_CHOICES = [
        ('active', 'アクティブ'),
        ('cancelled', 'キャンセル'),
        ('expired', '期限切れ'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    auto_renew = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'subscriptions'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.plan}"

class Payment(models.Model):
    """
    支払い履歴モデル
    """
    PAYMENT_STATUS_CHOICES = [
        ('pending', _('処理中')),
        ('completed', _('完了')),
        ('failed', _('失敗')),
        ('refunded', _('返金済み')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name=_('サブスクリプション')
    )
    amount = models.DecimalField(
        _('金額'),
        max_digits=10,
        decimal_places=2
    )
    currency = models.CharField(_('通貨'), max_length=3, default='JPY')
    status = models.CharField(
        _('ステータス'),
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )
    payment_method = models.CharField(_('支払い方法'), max_length=50)
    transaction_id = models.CharField(_('取引ID'), max_length=100, unique=True)
    created_at = models.DateTimeField(_('作成日時'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新日時'), auto_now=True)

    class Meta:
        verbose_name = _('支払い履歴')
        verbose_name_plural = _('支払い履歴')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.subscription.user.username} - {self.amount} {self.currency} ({self.status})" 