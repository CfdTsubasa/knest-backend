#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'knest_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from knest_backend.apps.circles.models import Circle

User = get_user_model()

print('✅ Django環境正常')
print(f'📊 ユーザー数: {User.objects.count()}')
print(f'📊 サークル数: {Circle.objects.count()}')

# テストユーザーを取得
test_user = User.objects.filter(username__startswith='testuser_').first()
if test_user:
    print(f'👤 テストユーザー: {test_user.username}')
    
    # フォールバック推薦テスト
    try:
        from knest_backend.apps.circles.recommendation import get_personalized_recommendations
        circles = get_personalized_recommendations(test_user, limit=3)
        print(f'🎯 フォールバック推薦成功: {len(circles)}件')
        for i, circle in enumerate(circles):
            print(f'  {i+1}. {circle.name}')
    except Exception as e:
        print(f'❌ フォールバック推薦エラー: {e}')
else:
    print('⚠️ テストユーザーが見つかりません') 