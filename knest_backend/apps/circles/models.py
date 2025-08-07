import uuid
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from knest_backend.apps.interests.models import InterestTag

class Category(models.Model):
    """サークルのカテゴリーモデル"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('カテゴリー名'), max_length=50)
    description = models.TextField(_('説明'), blank=True)
    created_at = models.DateTimeField(_('作成日時'), auto_now_add=True)

    class Meta:
        verbose_name = _('カテゴリー')
        verbose_name_plural = _('カテゴリー')

    def __str__(self):
        return self.name

class Circle(models.Model):
    """
    サークルモデル
    """
    CIRCLE_STATUS_CHOICES = [
        ('open', '募集中'),
        ('closed', '応募締切'),
        ('full', '満員'),
    ]

    CIRCLE_TYPE_CHOICES = [
        ('public', '公開'),
        ('approval', '承認制'),
        ('private', '非公開'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('サークル名'), max_length=100)
    description = models.TextField(_('説明'), blank=True)
    icon_url = models.URLField(_('アイコンURL'), max_length=500, blank=True, null=True)
    cover_url = models.URLField(_('カバー画像URL'), max_length=500, blank=True, null=True)
    categories = models.ManyToManyField(Category, related_name='circles', verbose_name=_('カテゴリー'))
    tags = models.JSONField(_('タグ'), default=list, blank=True)
    
    # 統計情報
    member_count = models.PositiveIntegerField(_('メンバー数'), default=0)
    post_count = models.PositiveIntegerField(_('投稿数'), default=0)
    last_activity = models.DateTimeField(_('最終アクティビティ'), auto_now=True)
    
    # 規約
    rules = models.TextField(_('サークル規約'), blank=True)
    
    status = models.CharField(
        _('募集状態'),
        max_length=20,
        choices=CIRCLE_STATUS_CHOICES,
        default='open'
    )
    circle_type = models.CharField(
        _('サークルタイプ'),
        max_length=20,
        choices=CIRCLE_TYPE_CHOICES,
        default='public'
    )
    is_premium = models.BooleanField(_('プレミアムサークル'), default=False)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_circles',
        verbose_name=_('作成者')
    )
    member_limit = models.IntegerField(_('メンバー制限'), null=True, blank=True)
    is_private = models.BooleanField(_('非公開'), default=False)
    created_at = models.DateTimeField(_('作成日時'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新日時'), auto_now=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='owned_circles',
        verbose_name=_('オーナー')
    )
    interests = models.ManyToManyField(
        'interests.InterestTag',
        through='CircleInterest',
        related_name='circles',
        verbose_name=_('興味・関心')
    )

    class Meta:
        verbose_name = _('サークル')
        verbose_name_plural = _('サークル')
        ordering = ['-last_activity']

    def __str__(self):
        return self.name

    def clean(self):
        # メンバー数が上限に達している場合、ステータスを自動的に'full'に設定
        if self.members.count() >= 10 and self.status != 'full':
            self.status = 'full'

        # メンバー数の上限チェック
        if self.member_count > 10:
            raise ValidationError(_('メンバー数が上限（10名）を超えています。'))

class CircleInterest(models.Model):
    """
    サークルと興味の関連モデル
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    circle = models.ForeignKey(
        Circle,
        on_delete=models.CASCADE,
        related_name='circle_interests',
        verbose_name=_('サークル')
    )
    interest = models.ForeignKey(
        'interests.InterestTag',
        on_delete=models.CASCADE,
        related_name='circle_interests',
        verbose_name=_('興味')
    )
    relevance_score = models.FloatField(_('関連度スコア'), default=0.0)
    added_at = models.DateTimeField(_('追加日時'), auto_now_add=True)

    class Meta:
        verbose_name = _('サークルの興味')
        verbose_name_plural = _('サークルの興味')
        unique_together = ('circle', 'interest')

    def __str__(self):
        return f"{self.circle.name} - {self.interest.name}"

class CircleRecommendation(models.Model):
    """
    サークルレコメンデーションモデル
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='circle_recommendations',
        verbose_name=_('ユーザー')
    )
    circle = models.ForeignKey(
        Circle,
        on_delete=models.CASCADE,
        related_name='recommendations',
        verbose_name=_('サークル')
    )
    recommendation_score = models.FloatField(_('レコメンドスコア'))
    recommendation_reason = models.CharField(_('レコメンド理由'), max_length=100)
    created_at = models.DateTimeField(_('作成日時'), auto_now_add=True)
    is_viewed = models.BooleanField(_('閲覧済み'), default=False)

    class Meta:
        verbose_name = _('サークルレコメンデーション')
        verbose_name_plural = _('サークルレコメンデーション')

class CircleMembership(models.Model):
    """
    サークルメンバーシップモデル
    """
    MEMBERSHIP_STATUS_CHOICES = [
        ('pending', '申請中'),
        ('active', '参加中'),
        ('rejected', '拒否'),
    ]

    ROLE_CHOICES = [
        ('owner', 'オーナー'),
        ('admin', '管理者'),
        ('member', 'メンバー'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='circle_memberships',
        verbose_name=_('ユーザー')
    )
    circle = models.ForeignKey(
        Circle,
        on_delete=models.CASCADE,
        related_name='memberships',
        verbose_name=_('サークル')
    )
    status = models.CharField(
        _('ステータス'),
        max_length=20,
        choices=MEMBERSHIP_STATUS_CHOICES,
        default='pending'
    )
    role = models.CharField(
        _('役割'),
        max_length=20,
        choices=ROLE_CHOICES,
        default='member'
    )
    joined_at = models.DateTimeField(_('参加日時'), null=True, blank=True)
    application_message = models.TextField(_('申請メッセージ'), blank=True)
    rejection_reason = models.TextField(_('拒否理由'), blank=True)

    class Meta:
        verbose_name = _('サークルメンバーシップ')
        verbose_name_plural = _('サークルメンバーシップ')
        unique_together = ['user', 'circle']
        ordering = ['-joined_at']

    def __str__(self):
        return f"{self.user.username} - {self.circle.name}"

    def clean(self):
        # アクティブなメンバーシップ数のチェック
        if self.status == 'active':
            active_memberships = CircleMembership.objects.filter(
                user=self.user,
                status='active'
            ).exclude(pk=self.pk).count()
            
            if active_memberships >= 4:
                raise ValidationError(
                    _('サークルの参加上限（4つ）に達しています。')
                )

            # サークルのメンバー数チェック
            circle_members = CircleMembership.objects.filter(
                circle=self.circle,
                status='active'
            ).exclude(pk=self.pk).count()
            
            if circle_members >= 10:
                raise ValidationError(
                    _('このサークルは既に満員（10人）です。')
                )

        # ユーザーのサークル参加数制限チェック
        user_circle_count = CircleMembership.objects.filter(user=self.user).count()
        max_circles = 4 if self.user.is_premium else 2
        if user_circle_count >= max_circles:
            raise ValidationError(_('参加可能なサークル数の上限に達しています。'))

    def save(self, *args, **kwargs):
        # 初めてactiveになる時に参加日時を設定
        if self.status == 'active' and not self.joined_at:
            self.joined_at = timezone.now()
        super().save(*args, **kwargs)

class CircleSearchHistory(models.Model):
    """
    サークル検索履歴モデル
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='circle_search_history',
        verbose_name=_('ユーザー')
    )
    search_query = models.CharField(_('検索クエリ'), max_length=200)
    search_filters = models.JSONField(_('検索フィルター'), default=dict)
    results_count = models.IntegerField(_('検索結果数'))
    searched_at = models.DateTimeField(_('検索日時'), auto_now_add=True)

    class Meta:
        verbose_name = _('サークル検索履歴')
        verbose_name_plural = _('サークル検索履歴')
        ordering = ['-searched_at']

    def __str__(self):
        return f"{self.user.username} - {self.search_query} ({self.searched_at.strftime('%Y-%m-%d %H:%M')})"

class CirclePost(models.Model):
    """サークル投稿モデル"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    circle = models.ForeignKey(Circle, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='circle_posts')
    content = models.TextField(_('内容'))
    media_urls = models.JSONField(_('メディアURL'), default=list, blank=True)
    created_at = models.DateTimeField(_('作成日時'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新日時'), auto_now=True)

    class Meta:
        verbose_name = _('サークル投稿')
        verbose_name_plural = _('サークル投稿')

class CircleEvent(models.Model):
    """サークルイベントモデル"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    circle = models.ForeignKey(Circle, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(_('タイトル'), max_length=200)
    description = models.TextField(_('説明'))
    start_datetime = models.DateTimeField(_('開始日時'))
    end_datetime = models.DateTimeField(_('終了日時'))
    location = models.CharField(_('場所'), max_length=200, blank=True)
    created_at = models.DateTimeField(_('作成日時'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新日時'), auto_now=True)

    class Meta:
        verbose_name = _('サークルイベント')
        verbose_name_plural = _('サークルイベント')

class CircleChat(models.Model):
    """サークルチャットモデル"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    circle = models.ForeignKey(Circle, on_delete=models.CASCADE, related_name='chats')
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='circle_chat_messages'
    )
    content = models.TextField(_('メッセージ内容'))
    media_urls = models.JSONField(_('メディアURL'), default=list, blank=True)
    created_at = models.DateTimeField(_('作成日時'), auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(_('更新日時'), auto_now=True)
    is_system_message = models.BooleanField(_('システムメッセージ'), default=False)
    is_edited = models.BooleanField(_('編集済み'), default=False)
    reply_to = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='replies'
    )

    class Meta:
        verbose_name = _('サークルチャット')
        verbose_name_plural = _('サークルチャット')
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['circle', '-created_at']),
            models.Index(fields=['sender', 'circle']),
            models.Index(fields=['circle', 'is_system_message']),
        ]

    def __str__(self):
        return f"{self.sender.username} - {self.content[:50]}"

class CircleChatRead(models.Model):
    """チャットの既読管理モデル"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='circle_chat_reads'
    )
    circle = models.ForeignKey(Circle, on_delete=models.CASCADE, related_name='chat_reads')
    last_read = models.DateTimeField(_('最終既読時間'), auto_now=True)

    class Meta:
        verbose_name = _('チャット既読')
        verbose_name_plural = _('チャット既読')
        unique_together = ['user', 'circle']
        indexes = [
            models.Index(fields=['user', 'circle', 'last_read']),
            models.Index(fields=['circle', 'last_read']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.circle.name}" 