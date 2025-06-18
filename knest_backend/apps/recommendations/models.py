import uuid
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class UserRecommendationFeedback(models.Model):
    """ユーザーの推薦結果に対するフィードバック"""
    FEEDBACK_TYPES = [
        ('view', '閲覧'),
        ('click', 'クリック'),
        ('join_request', '参加申請'),
        ('join_success', '参加成功'),
        ('dismiss', '却下'),
        ('not_interested', '興味なし'),
        ('bookmark', 'ブックマーク'),
        ('share', 'シェア'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recommendation_feedbacks',
        verbose_name='ユーザー'
    )
    circle = models.ForeignKey(
        'circles.Circle',
        on_delete=models.CASCADE,
        related_name='recommendation_feedbacks',
        verbose_name='サークル'
    )
    feedback_type = models.CharField(
        max_length=20,
        choices=FEEDBACK_TYPES,
        verbose_name='フィードバックタイプ'
    )
    recommendation_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name='推薦スコア'
    )
    recommendation_algorithm = models.CharField(
        max_length=50,
        verbose_name='推薦アルゴリズム'
    )
    recommendation_reasons = models.JSONField(
        default=list,
        verbose_name='推薦理由'
    )
    session_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='セッションID'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    
    class Meta:
        db_table = 'user_recommendation_feedbacks'
        verbose_name = 'ユーザー推薦フィードバック'
        verbose_name_plural = 'ユーザー推薦フィードバック'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['circle', 'feedback_type']),
            models.Index(fields=['recommendation_algorithm', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.circle.name} ({self.feedback_type})"


class UserSimilarity(models.Model):
    """ユーザー間の類似度キャッシュ"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user1 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='similarities_as_user1',
        verbose_name='ユーザー1'
    )
    user2 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='similarities_as_user2',
        verbose_name='ユーザー2'
    )
    similarity_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name='類似度スコア'
    )
    calculation_method = models.CharField(
        max_length=50,
        default='cosine',
        verbose_name='計算手法'
    )
    calculated_at = models.DateTimeField(auto_now=True, verbose_name='計算日時')
    
    class Meta:
        db_table = 'user_similarities'
        verbose_name = 'ユーザー類似度'
        verbose_name_plural = 'ユーザー類似度'
        unique_together = ('user1', 'user2', 'calculation_method')
        indexes = [
            models.Index(fields=['user1', 'similarity_score']),
            models.Index(fields=['user2', 'similarity_score']),
            models.Index(fields=['calculated_at']),
        ]
    
    def __str__(self):
        return f"{self.user1.username} - {self.user2.username}: {self.similarity_score:.3f}"


class RecommendationExperiment(models.Model):
    """A/Bテスト実験管理"""
    EXPERIMENT_STATUS = [
        ('draft', '下書き'),
        ('active', '実行中'),
        ('paused', '一時停止'),
        ('completed', '完了'),
        ('cancelled', 'キャンセル'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name='実験名')
    description = models.TextField(verbose_name='説明')
    algorithm_config = models.JSONField(verbose_name='アルゴリズム設定')
    target_user_ratio = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name='対象ユーザー割合'
    )
    status = models.CharField(
        max_length=20,
        choices=EXPERIMENT_STATUS,
        default='draft',
        verbose_name='ステータス'
    )
    start_date = models.DateTimeField(verbose_name='開始日時')
    end_date = models.DateTimeField(verbose_name='終了日時')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_experiments',
        verbose_name='作成者'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')
    
    class Meta:
        db_table = 'recommendation_experiments'
        verbose_name = '推薦実験'
        verbose_name_plural = '推薦実験'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.status})"


class RecommendationMetrics(models.Model):
    """推薦システムのメトリクス記録"""
    METRIC_TYPES = [
        ('ctr', 'クリック率'),
        ('conversion_rate', 'コンバージョン率'),
        ('precision_at_k', 'Precision@K'),
        ('diversity_score', '多様性スコア'),
        ('novelty_score', '新規性スコア'),
        ('coverage_rate', 'カバレッジ率'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    metric_type = models.CharField(
        max_length=30,
        choices=METRIC_TYPES,
        verbose_name='メトリクスタイプ'
    )
    algorithm_name = models.CharField(max_length=50, verbose_name='アルゴリズム名')
    metric_value = models.FloatField(verbose_name='メトリクス値')
    user_segment = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name='ユーザーセグメント'
    )
    experiment = models.ForeignKey(
        RecommendationExperiment,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='metrics',
        verbose_name='実験'
    )
    measurement_date = models.DateField(verbose_name='測定日')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    
    class Meta:
        db_table = 'recommendation_metrics'
        verbose_name = '推薦メトリクス'
        verbose_name_plural = '推薦メトリクス'
        indexes = [
            models.Index(fields=['metric_type', 'algorithm_name', 'measurement_date']),
            models.Index(fields=['experiment', 'metric_type']),
        ]
    
    def __str__(self):
        return f"{self.algorithm_name} - {self.metric_type}: {self.metric_value}"


class UserInteractionHistory(models.Model):
    """ユーザーのサークル関連アクション履歴"""
    ACTION_TYPES = [
        ('view_circle', 'サークル閲覧'),
        ('view_profile', 'プロフィール閲覧'),
        ('join_request', '参加申請'),
        ('join_approved', '参加承認'),
        ('join_rejected', '参加拒否'),
        ('leave_circle', 'サークル退会'),
        ('post_message', 'メッセージ投稿'),
        ('react_to_post', '投稿リアクション'),
        ('create_event', 'イベント作成'),
        ('join_event', 'イベント参加'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='interaction_history',
        verbose_name='ユーザー'
    )
    circle = models.ForeignKey(
        'circles.Circle',
        on_delete=models.CASCADE,
        related_name='interaction_history',
        verbose_name='サークル'
    )
    action_type = models.CharField(
        max_length=30,
        choices=ACTION_TYPES,
        verbose_name='アクションタイプ'
    )
    duration_seconds = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='滞在時間（秒）'
    )
    context_data = models.JSONField(
        default=dict,
        verbose_name='コンテキストデータ'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    
    class Meta:
        db_table = 'user_interaction_history'
        verbose_name = 'ユーザーインタラクション履歴'
        verbose_name_plural = 'ユーザーインタラクション履歴'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['circle', 'action_type']),
            models.Index(fields=['action_type', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.action_type} - {self.circle.name}" 