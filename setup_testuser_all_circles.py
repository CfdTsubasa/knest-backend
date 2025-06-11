#!/usr/bin/env python
"""
testuserを全てのサークルに参加させるスクリプト
manage.py shell で実行してください
"""

import os
import django
from datetime import date

# Django設定
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'knest_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from knest_backend.apps.circles.models import Circle, CircleMembership
from knest_backend.apps.interests.models import InterestTag, UserInterestProfile

User = get_user_model()

def setup_testuser_all_circles():
    """testuserを全サークルに参加状態にする"""
    
    print("🚀 testuserを全サークル参加状態にセットアップ中...")
    
    # testuserを取得または作成
    test_user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com',
            'display_name': 'テストユーザー（全サークル参加済み）',
            'birth_date': date(1995, 5, 15),
            'prefecture': 'tokyo'
        }
    )
    
    if created:
        test_user.set_password('testpass123')
        test_user.save()
        print(f"✅ testuserを新規作成しました")
    else:
        # 既存ユーザーのプロフィール更新
        test_user.display_name = 'テストユーザー（全サークル参加済み）'
        test_user.birth_date = date(1995, 5, 15)
        test_user.prefecture = 'tokyo'
        test_user.save()
        print(f"✅ testuserのプロフィールを更新しました")
    
    # サークルが存在しない場合はダミーサークルを作成
    all_circles = Circle.objects.all()
    print(f"📊 既存サークル数: {all_circles.count()}個")
    
    if all_circles.count() == 0:
        print("📝 サークルが存在しないため、テスト用サークルを作成します...")
        
        # テスト用サークルを作成
        test_circles = [
            {
                'name': 'iOS開発サークル',
                'description': 'iOSアプリ開発を学ぶサークルです',
                'status': 'open'
            },
            {
                'name': 'デザイン研究会',
                'description': 'UI/UXデザインを学ぶ研究会です',
                'status': 'open'
            },
            {
                'name': 'フットサル同好会',
                'description': '毎週末フットサルを楽しんでいます',
                'status': 'open'
            },
            {
                'name': 'カフェ巡りの会',
                'description': '都内のおしゃれなカフェを巡ります',
                'status': 'open'
            },
            {
                'name': '読書クラブ',
                'description': '月1冊の本を読んで感想を共有します',
                'status': 'open'
            }
        ]
        
        created_circles = []
        for circle_data in test_circles:
            circle = Circle.objects.create(
                name=circle_data['name'],
                description=circle_data['description'],
                status=circle_data['status'],
                creator=test_user,
                owner=test_user
            )
            created_circles.append(circle)
            print(f"  ✅ '{circle.name}' を作成しました")
        
        all_circles = Circle.objects.all()
        print(f"📊 サークル作成完了: {all_circles.count()}個")
    
    # testuserを全サークルに参加させる
    joined_count = 0
    already_joined_count = 0
    
    for circle in all_circles:
        membership, created = CircleMembership.objects.get_or_create(
            circle=circle,
            user=test_user,
            defaults={
                'role': 'member',
                'status': 'active'
            }
        )
        
        if created:
            joined_count += 1
            print(f"  ✅ '{circle.name}' に参加しました")
        else:
            already_joined_count += 1
            print(f"  📌 '{circle.name}' には既に参加済みです")
    
    print(f"\n🎉 testuserのサークル参加状況:")
    print(f"  新規参加: {joined_count}個")
    print(f"  既参加済み: {already_joined_count}個")
    print(f"  総参加数: {joined_count + already_joined_count}個")
    
    # 興味関心もいくつか追加（マッチング確認用）
    setup_testuser_interests(test_user)
    
    print(f"\n✅ testuserが全{all_circles.count()}サークルに参加完了！")
    print(f"📱 ログイン情報:")
    print(f"  ユーザー名: testuser")
    print(f"  パスワード: testpass123")
    print(f"  メール: test@example.com")

def setup_testuser_interests(test_user):
    """testuserに興味関心を設定"""
    
    print(f"\n🎯 testuserの興味関心を設定中...")
    
    # 既存のユーザー興味関心の数を確認
    existing_interests = UserInterestProfile.objects.filter(user=test_user)
    print(f"📊 既存の興味関心数: {existing_interests.count()}個")
    
    for interest in existing_interests:
        print(f"  - {interest.tag.name} (強度: {interest.intensity})")

# 実行
if __name__ == '__main__':
    setup_testuser_all_circles() 