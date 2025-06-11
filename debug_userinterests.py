#!/usr/bin/env python
"""
ユーザー興味データのデバッグ用スクリプト
"""

import os
import sys
import django

# Django設定
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'knest_backend.settings')
django.setup()

from knest_backend.apps.interests.models import UserInterest, Interest
from django.contrib.auth import get_user_model

def debug_user_interests():
    User = get_user_model()
    
    print("=== ユーザー興味データのデバッグ ===")
    
    # 全ユーザーを表示
    users = User.objects.all()
    print(f"📊 全ユーザー数: {users.count()}")
    for user in users:
        print(f"  - {user.username} (ID: {user.id})")
    
    # testユーザーの興味を表示
    try:
        test_user = User.objects.get(username='testuser')
        print(f"\n📱 testuserの興味:")
        user_interests = UserInterest.objects.filter(user=test_user)
        print(f"  興味数: {user_interests.count()}")
        
        for ui in user_interests:
            print(f"  - {ui.interest.name} (ID: {ui.id}, Interest ID: {ui.interest.id})")
            
    except User.DoesNotExist:
        print("❌ testuserが存在しません")
    
    # 全UserInterestを表示
    print(f"\n📋 全UserInterest数: {UserInterest.objects.count()}")
    for ui in UserInterest.objects.all():
        print(f"  - {ui.user.username}: {ui.interest.name} (ID: {ui.id})")

if __name__ == "__main__":
    debug_user_interests() 