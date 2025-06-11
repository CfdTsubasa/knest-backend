#!/usr/bin/env python

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'knest_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from knest_backend.apps.circles.models import Circle, CircleMembership
from datetime import date

User = get_user_model()

print("🚀 testuserセットアップ開始...")

# testuserを作成/更新
user, created = User.objects.get_or_create(
    username='testuser',
    defaults={
        'email': 'test@example.com',
        'display_name': 'テストユーザー（全サークル参加済み）',
        'birth_date': date(1995, 5, 15),
        'prefecture': 'tokyo'
    }
)

if created:
    user.set_password('testpass123')
    user.save()
    print("✅ testuserを新規作成")
else:
    user.display_name = 'テストユーザー（全サークル参加済み）'
    user.birth_date = date(1995, 5, 15)
    user.prefecture = 'tokyo'
    user.save()
    print("✅ testuserを更新")

# サークルが存在しない場合は作成
circles = Circle.objects.all()
print(f"📊 既存サークル数: {circles.count()}")

if circles.count() == 0:
    print("📝 テスト用サークルを作成...")
    
    test_circles = [
        ('iOS開発サークル', 'iOSアプリ開発を学ぶサークルです'),
        ('デザイン研究会', 'UI/UXデザインを学ぶ研究会です'),
        ('フットサル同好会', '毎週末フットサルを楽しんでいます'),
        ('カフェ巡りの会', '都内のおしゃれなカフェを巡ります'),
        ('読書クラブ', '月1冊の本を読んで感想を共有します')
    ]
    
    for name, desc in test_circles:
        circle = Circle.objects.create(
            name=name,
            description=desc,
            status='open',
            creator=user,
            owner=user
        )
        print(f"  ✅ '{name}' 作成完了")

# 全サークルを取得
all_circles = Circle.objects.all()
print(f"📊 総サークル数: {all_circles.count()}")

# testuserを全サークルに参加
joined = 0
for circle in all_circles:
    membership, created = CircleMembership.objects.get_or_create(
        circle=circle,
        user=user,
        defaults={'role': 'member', 'status': 'active'}
    )
    if created:
        joined += 1
        print(f"  ✅ '{circle.name}' に参加")

print(f"\n🎉 セットアップ完了！")
print(f"  新規参加: {joined}個")
print(f"  総参加数: {all_circles.count()}個")
print(f"\n📱 ログイン情報:")
print(f"  ユーザー名: testuser")
print(f"  パスワード: testpass123")
print(f"  メール: test@example.com") 