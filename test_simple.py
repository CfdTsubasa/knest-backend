#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'knest_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from knest_backend.apps.circles.models import Circle
from knest_backend.apps.users.models import User

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

try:
    user_count = User.objects.count()
    circle_count = Circle.objects.count()
    print(f"ユーザー数: {user_count}")
    print(f"サークル数: {circle_count}")
    
    if user_count > 0:
        user = User.objects.first()
        print(f"テストユーザー: {user.username}")
        
        # 推薦エンジンをテスト
        from knest_backend.apps.recommendations.engines import NextGenRecommendationEngine
        engine = NextGenRecommendationEngine(user)
        
        # アルゴリズム重みを確認
        weights = engine.calculate_algorithm_weights()
        print(f"アルゴリズム重み: {weights}")
        
        # 簡単な推薦テスト
        recommendations = engine.generate_recommendations(algorithm='smart', limit=3)
        print(f"推薦結果数: {len(recommendations['recommendations'])}")
        print(f"総候補数: {recommendations['total_candidates']}")
        print(f"計算時間: {recommendations['computation_time_ms']:.2f}ms")
        
        # 各推薦の詳細
        for i, rec in enumerate(recommendations['recommendations'], 1):
            circle = rec['circle']
            score = rec['score']
            confidence = rec['confidence']
            score_breakdown = rec.get('score_breakdown', {})
            
            print(f"\n{i}. {circle.name}")
            print(f"   スコア: {score:.3f}, 信頼度: {confidence:.3f}")
            print(f"   メンバー数: {circle.member_count}")
            
            if score_breakdown:
                total = score_breakdown.get('total', score)
                hierarchical = score_breakdown.get('hierarchical', 0)
                collaborative = score_breakdown.get('collaborative', 0)
                behavioral = score_breakdown.get('behavioral', 0)
                popularity = score_breakdown.get('popularity', 0)
                
                print(f"   興味関心: {hierarchical:.3f} ({hierarchical/total*100:.1f}%)")
                print(f"   類似ユーザー: {collaborative:.3f} ({collaborative/total*100:.1f}%)")
                print(f"   行動パターン: {behavioral:.3f} ({behavioral/total*100:.1f}%)")
                print(f"   人気度: {popularity:.3f} ({popularity/total*100:.1f}%)")
                
                # 人気度の比率を分析
                popularity_ratio = (popularity / total * 100) if total > 0 else 0
                if popularity_ratio > 20:
                    print(f"   ⚠️ 人気度の影響が大きい: {popularity_ratio:.1f}%")
                else:
                    print(f"   ✅ 多要素評価: 人気度は{popularity_ratio:.1f}%のみ")
    else:
        print("データがありません")
        
except Exception as e:
    print(f"エラー: {e}")
    import traceback
    traceback.print_exc() 