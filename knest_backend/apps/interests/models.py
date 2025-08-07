import uuid
from django.db import models
from django.conf import settings

# ======================================
# 新しい3階層興味関心システム用モデル
# ======================================

class InterestCategory(models.Model):
    """興味関心カテゴリ（第1階層）"""
    TYPE_CHOICES = [
        ('hobby', '趣味'),
        ('skill', 'スキル'),
        ('career', 'キャリア'),
        ('lifestyle', 'ライフスタイル'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, verbose_name='カテゴリ名')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name='タイプ')
    description = models.TextField(null=True, blank=True, verbose_name='説明')
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
    description = models.TextField(null=True, blank=True, verbose_name='説明')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    
    class Meta:
        db_table = 'interest_subcategories'
        verbose_name = '興味関心サブカテゴリ'
        verbose_name_plural = '興味関心サブカテゴリ'
        ordering = ['category', 'name']
        unique_together = ('category', 'name')
    
    def __str__(self):
        return f"{self.category.name} - {self.name}"

class InterestTag(models.Model):
    """興味関心タグ（第3階層）"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subcategory = models.ForeignKey(InterestSubcategory, on_delete=models.CASCADE, related_name='tags', verbose_name='サブカテゴリ')
    name = models.CharField(max_length=100, verbose_name='タグ名')
    description = models.TextField(null=True, blank=True, verbose_name='説明')
    usage_count = models.IntegerField(default=0, verbose_name='使用回数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    
    class Meta:
        db_table = 'interest_tags'
        verbose_name = '興味関心タグ'
        verbose_name_plural = '興味関心タグ'
        ordering = ['subcategory', '-usage_count', 'name']
        unique_together = ('subcategory', 'name')
    
    def __str__(self):
        return f"{self.subcategory.category.name} - {self.subcategory.name} - {self.name}"

class UserInterestProfile(models.Model):
    """ユーザーの興味関心プロフィール（階層レベル選択可能）"""
    LEVEL_CHOICES = [
        (1, 'カテゴリレベル'),
        (2, 'サブカテゴリレベル'),
        (3, 'タグレベル'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='hierarchical_interests', verbose_name='ユーザー')
    category = models.ForeignKey(InterestCategory, on_delete=models.CASCADE, verbose_name='カテゴリ')
    subcategory = models.ForeignKey(InterestSubcategory, on_delete=models.CASCADE, null=True, blank=True, verbose_name='サブカテゴリ')
    tag = models.ForeignKey(InterestTag, on_delete=models.CASCADE, null=True, blank=True, verbose_name='タグ')
    level = models.IntegerField(choices=LEVEL_CHOICES, default=3, verbose_name='選択レベル')
    added_at = models.DateTimeField(auto_now_add=True, verbose_name='追加日時')
    
    class Meta:
        db_table = 'user_interest_profiles'
        verbose_name = 'ユーザー興味関心プロフィール'
        verbose_name_plural = 'ユーザー興味関心プロフィール'
        ordering = ['-added_at']
    
    def __str__(self):
        if self.tag:
            return f"{self.user.username} - {self.tag.name} (タグレベル)"
        elif self.subcategory:
            return f"{self.user.username} - {self.subcategory.name} (サブカテゴリレベル)"
        else:
            return f"{self.user.username} - {self.category.name} (カテゴリレベル)"

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