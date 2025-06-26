#!/usr/bin/env python
import os
import sys
import django

# Djangoの設定を初期化
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'knest_backend.settings')
django.setup()

from knest_backend.apps.users.models import User
from knest_backend.apps.circles.models import Circle, CircleMembership

def check_user_membership():
    try:
        # testuser6363ユーザーを取得
        user = User.objects.get(username='testuser6363')
        print(f"✅ ユーザー確認: {user.username} (ID: {user.id})")
        
        # ユーザーの参加サークルを確認
        memberships = CircleMembership.objects.filter(user=user)
        print(f"\n🎯 参加サークル数: {memberships.count()}")
        
        for membership in memberships:
            print(f"  - {membership.circle.name} (ID: {membership.circle.id})")
            print(f"    役割: {membership.role}")
            print(f"    参加日: {membership.joined_at}")
            print(f"    ステータス: {membership.status}")
            print()
        
        # API用の確認
        print("📡 API レスポンス確認:")
        for membership in memberships:
            circle = membership.circle
            print(f"  サークル: {circle.name}")
            print(f"    ID: {circle.id}")
            print(f"    タイプ: {circle.circle_type}")
            print(f"    ステータス: {circle.status}")
            print(f"    作成者: {circle.created_by.username}")
            print()
            
        # 全サークル確認
        all_circles = Circle.objects.all()
        print(f"📊 全サークル数: {all_circles.count()}")
        for circle in all_circles:
            is_member = CircleMembership.objects.filter(user=user, circle=circle).exists()
            print(f"  - {circle.name}: {'参加中' if is_member else '未参加'}")
            
    except User.DoesNotExist:
        print("❌ testuser6363ユーザーが見つかりません")
    except Exception as e:
        print(f"❌ エラー: {e}")

if __name__ == '__main__':
    check_user_membership() 