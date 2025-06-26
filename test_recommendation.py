#!/usr/bin/env python
"""
推薦システムのテストスクリプト
各要素の寄与度を詳細に表示する
"""
import os
import sys
import django

# Django設定
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'knest_backend.settings')
django.setup()

from knest_backend.apps.users.models import User
from knest_backend.apps.recommendations.engines import NextGenRecommendationEngine
import logging

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger('knest_backend.apps.recommendations.engines')
logger.setLevel(logging.INFO)

def test_recommendation_system():
    """推薦システムをテストして詳細ログを表示"""
    try:
        # テストユーザーを取得
        user = User.objects.first()
        if not user:
            print("❌ テストユーザーが見つかりませんでした")
            return
            
        print(f"🧪 テストユーザー: {user.username}")
        print(f"📧 メールアドレス: {user.email}")
        print("=" * 60)
        
        # 推薦エンジンを初期化
        engine = NextGenRecommendationEngine(user)
        
        # 推薦を生成（詳細ログ付き）
        recommendations = engine.generate_recommendations(
            algorithm='smart',
            limit=5
        )
        
        print("\n📊 === 最終結果サマリー ===")
        print(f"アルゴリズム重み: {recommendations['algorithm_weights']}")
        print(f"総候補数: {recommendations['total_candidates']}")
        print(f"計算時間: {recommendations['computation_time_ms']:.2f}ms")
        
        print("\n🎯 === 推薦されたサークル ===")
        for i, rec in enumerate(recommendations['recommendations'], 1):
            circle = rec['circle']
            score_breakdown = rec.get('score_breakdown', {})
            
            print(f"\n{i}. 【{circle.name}】")
            print(f"   総合スコア: {rec['score']:.3f}")
            print(f"   信頼度: {rec['confidence']:.3f}")
            print(f"   メンバー数: {circle.member_count}人")
            
            if score_breakdown:
                total = score_breakdown.get('total', rec['score'])
                print(f"   --- スコア内訳 ---")
                hierarchical = score_breakdown.get('hierarchical', 0)
                collaborative = score_breakdown.get('collaborative', 0)
                behavioral = score_breakdown.get('behavioral', 0)
                diversity = score_breakdown.get('diversity', 0)
                popularity = score_breakdown.get('popularity', 0)
                
                print(f"   興味関心マッチ: {hierarchical:.3f} ({hierarchical/total*100:.1f}%)")
                print(f"   類似ユーザー: {collaborative:.3f} ({collaborative/total*100:.1f}%)")
                print(f"   行動パターン: {behavioral:.3f} ({behavioral/total*100:.1f}%)")
                print(f"   多様性保証: {diversity:.3f} ({diversity/total*100:.1f}%)")
                print(f"   人気度ボーナス: {popularity:.3f} ({popularity/total*100:.1f}%)")
                
                # 主要な寄与要素を特定
                main_contributors = []
                if hierarchical > 0:
                    main_contributors.append(f"興味関心マッチ({hierarchical/total*100:.0f}%)")
                if collaborative > 0:
                    main_contributors.append(f"類似ユーザー({collaborative/total*100:.0f}%)")
                if behavioral > 0:
                    main_contributors.append(f"行動パターン({behavioral/total*100:.0f}%)")
                if popularity > 0:
                    main_contributors.append(f"人気度({popularity/total*100:.0f}%)")
                
                print(f"   >>> 主要因: {', '.join(main_contributors)}")
            
            # 推薦理由
            reasons = rec.get('reasons', [])
            if reasons:
                print(f"   --- 推薦理由 ---")
                for j, reason in enumerate(reasons, 1):
                    print(f"   {j}. {reason['detail']}")
                    if reason.get('explanation'):
                        print(f"      → {reason['explanation']}")
        
        # 人気度だけでおすすめされているかの分析
        print("\n🔍 === 人気度分析 ===")
        popularity_only_count = 0
        total_recommendations = len(recommendations['recommendations'])
        
        for rec in recommendations['recommendations']:
            score_breakdown = rec.get('score_breakdown', {})
            if score_breakdown:
                total = score_breakdown.get('total', rec['score'])
                popularity = score_breakdown.get('popularity', 0)
                other_factors = total - popularity
                
                popularity_percentage = (popularity / total * 100) if total > 0 else 0
                
                if popularity_percentage > 50:  # 人気度が50%以上
                    popularity_only_count += 1
                    print(f"⚠️  [{rec['circle']['name']}] 人気度主導: {popularity_percentage:.1f}%")
                else:
                    print(f"✅ [{rec['circle']['name']}] 多要素評価: 人気度は{popularity_percentage:.1f}%のみ")
        
        print(f"\n📈 結論:")
        print(f"人気度主導の推薦: {popularity_only_count}/{total_recommendations} ({popularity_only_count/total_recommendations*100:.1f}%)")
        print(f"多要素評価の推薦: {total_recommendations - popularity_only_count}/{total_recommendations} ({(total_recommendations - popularity_only_count)/total_recommendations*100:.1f}%)")
        
        if popularity_only_count == 0:
            print("🎉 人気度だけでおすすめされているサークルはありません！")
        else:
            print(f"⚠️  {popularity_only_count}件のサークルが人気度主導で推薦されています")
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_recommendation_system() 