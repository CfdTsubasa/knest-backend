import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

# 都道府県の選択肢
PREFECTURE_CHOICES = [
    ('hokkaido', '北海道'),
    ('aomori', '青森県'),
    ('iwate', '岩手県'),
    ('miyagi', '宮城県'),
    ('akita', '秋田県'),
    ('yamagata', '山形県'),
    ('fukushima', '福島県'),
    ('ibaraki', '茨城県'),
    ('tochigi', '栃木県'),
    ('gunma', '群馬県'),
    ('saitama', '埼玉県'),
    ('chiba', '千葉県'),
    ('tokyo', '東京都'),
    ('kanagawa', '神奈川県'),
    ('niigata', '新潟県'),
    ('toyama', '富山県'),
    ('ishikawa', '石川県'),
    ('fukui', '福井県'),
    ('yamanashi', '山梨県'),
    ('nagano', '長野県'),
    ('gifu', '岐阜県'),
    ('shizuoka', '静岡県'),
    ('aichi', '愛知県'),
    ('mie', '三重県'),
    ('shiga', '滋賀県'),
    ('kyoto', '京都府'),
    ('osaka', '大阪府'),
    ('hyogo', '兵庫県'),
    ('nara', '奈良県'),
    ('wakayama', '和歌山県'),
    ('tottori', '鳥取県'),
    ('shimane', '島根県'),
    ('okayama', '岡山県'),
    ('hiroshima', '広島県'),
    ('yamaguchi', '山口県'),
    ('tokushima', '徳島県'),
    ('kagawa', '香川県'),
    ('ehime', '愛媛県'),
    ('kochi', '高知県'),
    ('fukuoka', '福岡県'),
    ('saga', '佐賀県'),
    ('nagasaki', '長崎県'),
    ('kumamoto', '熊本県'),
    ('oita', '大分県'),
    ('miyazaki', '宮崎県'),
    ('kagoshima', '鹿児島県'),
    ('okinawa', '沖縄県'),
]

class User(AbstractUser):
    """
    カスタムユーザーモデル
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    display_name = models.CharField(_('表示名'), max_length=150, blank=True)
    avatar_url = models.URLField(_('アバターURL'), max_length=500, blank=True, null=True)
    bio = models.TextField(_('自己紹介'), blank=True, null=True)
    emotion_state = models.CharField(_('現在の気分'), max_length=100, blank=True, null=True)
    is_premium = models.BooleanField(_('プレミアム会員'), default=False)
    last_active = models.DateTimeField(_('最終アクティブ'), auto_now=True)
    created_at = models.DateTimeField(_('作成日時'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新日時'), auto_now=True)
    
    # マッチング機能のための新フィールド
    birth_date = models.DateField(_('生年月日'), null=True, blank=True)
    prefecture = models.CharField(_('都道府県'), max_length=20, choices=PREFECTURE_CHOICES, null=True, blank=True)
    
    # パスワードリセット用フィールド
    password_reset_token = models.CharField(max_length=64, null=True, blank=True)
    password_reset_token_created = models.DateTimeField(null=True, blank=True)
    # aaa@hmail.cpm

    class Meta:
        verbose_name = _('ユーザー')
        verbose_name_plural = _('ユーザー')

    def __str__(self):
        return self.display_name or self.username
    
    @property
    def age(self):
        """年齢を計算して返す"""
        if not self.birth_date:
            return None
        from datetime import date
        today = date.today()
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day)) 