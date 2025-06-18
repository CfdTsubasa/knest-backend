#!/usr/bin/env python
"""
マッチングAPIのテストスクリプト
"""
import os
import sys
import django

# Djangoの設定
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'knest_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from knest_backend.apps.circles.models import Circle
from knest_backend.apps.interests.models import UserInterestProfile, InterestTag
from knest_backend.apps.recommendations.engines import NextGenRecommendationEngine

User = get_user_model()

def test_matching_api():
    """マッチングAPIのテスト"""
    print("🧪 マッチングAPIテスト開始")
    
    # テストユーザーを取得（存在しない場合は作成）
    try:
        test_user = User.objects.filter(username__startswith='testuser_').first()
        if not test_user:
            test_user = User.objects.create_user(
                username='testuser_api_test',
                email='test@example.com',
                password='testpass123'
            )
            print(f"✅ テストユーザー作成: {test_user.username}")
        else:
            print(f"✅ 既存テストユーザー使用: {test_user.username}")
    except Exception as e:
        print(f"❌ テストユーザー準備エラー: {e}")
        return
    
    # サークル数を確認
    circle_count = Circle.objects.count()
    print(f"📊 システム内サークル数: {circle_count}")
    
    if circle_count == 0:
        print("⚠️ サークルが存在しません。テストサークルを作成中...")
        # 簡単なテストサークルを作成
        try:
            test_circle = Circle.objects.create(
                name="テストプログラミングサークル",
                description="プログラミングを楽しく学ぶサークルです",
                creator=test_user,
                owner=test_user,
                status='open',
                circle_type='public'
            )
            print(f"✅ テストサークル作成: {test_circle.name}")
        except Exception as e:
            print(f"❌ テストサークル作成エラー: {e}")
    
    # 推薦エンジンのテスト
    try:
        print("🔍 推薦エンジンテスト開始...")
        engine = NextGenRecommendationEngine(test_user)
        
        # 基本推薦テスト
        recommendations = engine.generate_recommendations(
            algorithm='smart',
            limit=5,
            diversity_factor=0.3
        )
        
        print(f"✅ 推薦エンジン動作成功")
        print(f"📈 推薦結果数: {len(recommendations['recommendations'])}")
        print(f"⏱️ 計算時間: {recommendations['computation_time_ms']:.2f}ms")
        print(f"🎯 候補総数: {recommendations['total_candidates']}")
        
        # 推薦結果の詳細表示
        for i, rec in enumerate(recommendations['recommendations'][:3]):
            circle = rec['circle']
            score = rec['score']
            print(f"  {i+1}. {circle.name} (スコア: {score:.3f})")
        
    except Exception as e:
        print(f"❌ 推薦エンジンエラー: {e}")
        import traceback
        traceback.print_exc()
    
    # フォールバック推薦テスト
    try:
        print("🔄 フォールバック推薦テスト...")
        from knest_backend.apps.circles.recommendation import get_personalized_recommendations
        
        circles = get_personalized_recommendations(test_user, limit=5)
        print(f"✅ フォールバック推薦成功: {len(circles)}件")
        
        for i, circle in enumerate(circles[:3]):
            print(f"  {i+1}. {circle.name} (メンバー: {circle.member_count})")
            
    except Exception as e:
        print(f"❌ フォールバック推薦エラー: {e}")
    
    print("🏁 マッチングAPIテスト完了")

if __name__ == "__main__":
    test_matching_api() 