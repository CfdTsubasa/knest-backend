#!/usr/bin/env python3
"""
testuserとその関連データを削除するスクリプト
"""
import os
import django

# Django設定
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'knest_backend.settings.base')
django.setup()

from knest_backend.apps.users.models import User

def delete_testuser():
    """testuserとその関連データを削除"""
    print("🗑️ testuserとその関連データを削除中...")
    
    try:
        testuser = User.objects.get(username='testuser')
        print(f"🎯 発見: {testuser.username} (ID: {testuser.id})")
        
        # 関連データも含めて削除（Djangoの CASCADE DELETE）
        testuser.delete()
        print("✅ testuserとその関連データを削除しました")
        
    except User.DoesNotExist:
        print("⚠️ testuserは存在しませんでした")
    
    # 残りユーザー確認
    users = User.objects.all()
    print(f"\n📊 残りユーザー数: {users.count()}")
    for user in users:
        print(f"  - {user.username} (ID: {user.id})")

if __name__ == "__main__":
    delete_testuser() 