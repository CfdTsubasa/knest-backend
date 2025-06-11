import uuid
from django.db import models
from django.conf import settings

class Interest(models.Model):
    CATEGORY_CHOICES = [
        ('gaming', '🎮 ゲーム'),
        ('learning', '📚 学習・知識'),
        ('creative', '🎨 クリエイティブ'),
        ('sports', '🏃‍♂️ スポーツ'),
        ('food', '🍳 料理・グルメ'),
        ('travel', '🌍 旅行・アウトドア'),
        ('lifestyle', '💰 ライフスタイル'),
        ('entertainment', '🎭 エンターテイメント'),
        ('technical', '🔬 技術・専門'),
        ('business', '🎯 ビジネス・キャリア'),
        ('wellness', '🧠 自己開発・ウェルネス'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    is_official = models.BooleanField(default=False)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_interests'
    )
    usage_count = models.IntegerField(default=0)
    icon_url = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'interests'
        ordering = ['-usage_count', 'name']

    def __str__(self):
        return self.name

class UserInterest(models.Model):
    """ユーザーの興味関心（シンプル版）"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='selected_interests')
    interest = models.ForeignKey(Interest, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'interest')
        verbose_name = "ユーザー興味関心"
        verbose_name_plural = "ユーザー興味関心"
    
    def __str__(self):
        return f"{self.user.username} - {self.interest.name}"

class Tag(models.Model):
    """ハッシュタグモデル"""
    name = models.CharField(max_length=50, unique=True, db_index=True)
    usage_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-usage_count', 'name']
    
    def __str__(self):
        return f"#{self.name}"

class UserTag(models.Model):
    """ユーザーとハッシュタグの関連"""
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='user_tags')
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name='user_tags')
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'tag')
        ordering = ['-added_at']
    
    def __str__(self):
        return f"{self.user.username} - #{self.tag.name}"


# ======================================
# 新しい3階層興味関心システム
# ======================================

class InterestCategory(models.Model):
    """興味関心カテゴリ（第1階層）"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, verbose_name='カテゴリ名')
    type = models.CharField(max_length=50, verbose_name='タイプ')  # 技術系、スポーツ系など
    description = models.TextField(verbose_name='説明')
    icon_url = models.URLField(null=True, blank=True, verbose_name='アイコンURL')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    
    class Meta:
        db_table = 'interest_categories'
        verbose_name = '興味関心カテゴリ'
        verbose_name_plural = '興味関心カテゴリ'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class InterestSubcategory(models.Model):
    """興味関心サブカテゴリ（第2階層）"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(InterestCategory, on_delete=models.CASCADE, related_name='subcategories', verbose_name='カテゴリ')
    name = models.CharField(max_length=100, verbose_name='サブカテゴリ名')
    description = models.TextField(verbose_name='説明')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    
    class Meta:
        db_table = 'interest_subcategories'
        verbose_name = '興味関心サブカテゴリ'
        verbose_name_plural = '興味関心サブカテゴリ'
        unique_together = ('category', 'name')
        ordering = ['category__name', 'name']
    
    def __str__(self):
        return f"{self.category.name} > {self.name}"


class InterestTag(models.Model):
    """興味関心タグ（第3階層）"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subcategory = models.ForeignKey(InterestSubcategory, on_delete=models.CASCADE, related_name='tags', verbose_name='サブカテゴリ')
    name = models.CharField(max_length=100, verbose_name='タグ名')
    description = models.TextField(verbose_name='説明')
    usage_count = models.IntegerField(default=0, verbose_name='使用回数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    
    class Meta:
        db_table = 'interest_tags'
        verbose_name = '興味関心タグ'
        verbose_name_plural = '興味関心タグ'
        unique_together = ('subcategory', 'name')
        ordering = ['-usage_count', 'subcategory__category__name', 'subcategory__name', 'name']
    
    def __str__(self):
        return f"{self.subcategory.category.name} > {self.subcategory.name} > {self.name}"


class UserInterestProfile(models.Model):
    """ユーザーの興味関心プロフィール（強度付き）"""
    INTENSITY_CHOICES = [
        (1, '少し興味がある'),
        (2, '興味がある'),
        (3, 'かなり興味がある'),
        (4, 'とても興味がある'),
        (5, '非常に興味がある'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='hierarchical_interests', verbose_name='ユーザー')
    category = models.ForeignKey(InterestCategory, on_delete=models.CASCADE, null=True, blank=True, verbose_name='カテゴリ')
    subcategory = models.ForeignKey(InterestSubcategory, on_delete=models.CASCADE, null=True, blank=True, verbose_name='サブカテゴリ')
    tag = models.ForeignKey(InterestTag, on_delete=models.CASCADE, verbose_name='タグ')
    intensity = models.IntegerField(choices=INTENSITY_CHOICES, default=3, verbose_name='強度')
    added_at = models.DateTimeField(auto_now_add=True, verbose_name='追加日時')
    
    class Meta:
        db_table = 'user_interest_profiles'
        verbose_name = 'ユーザー興味関心プロフィール'
        verbose_name_plural = 'ユーザー興味関心プロフィール'
        unique_together = ('user', 'tag')
        ordering = ['-intensity', '-added_at']
    
    def save(self, *args, **kwargs):
        # tagの階層情報を自動設定
        if self.tag:
            self.subcategory = self.tag.subcategory
            self.category = self.tag.subcategory.category
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.username} - {self.tag.name} (強度: {self.intensity})" 