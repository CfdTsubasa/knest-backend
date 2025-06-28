#!/usr/bin/env python
"""
高一致度マッチング専用テストスクリプト
特定ユーザーの推薦結果を詳細分析
"""
import os
import sys
import django

# Django設定
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'knest_backend.settings.base')
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

def test_specific_user_recommendations(username):
    """特定ユーザーの推薦結果をテスト"""
    try:
        # 指定ユーザーを取得
        user = User.objects.get(username=username)
        print(f"🧪 テストユーザー: {user.username} ({user.display_name})")
        print(f"📧 メールアドレス: {user.email}")
        print(f"📍 都道府県: {user.prefecture}")
        print("=" * 80)
        
        # ユーザーの興味関心を表示
        interests = user.hierarchical_interests.all()
        if interests:
            print("🎯 ユーザーの興味関心:")
            for interest in interests:
                level_text = f"レベル{interest.level}" if hasattr(interest, 'level') else "レベル不明"
                intensity_text = f"強度{interest.intensity}" if hasattr(interest, 'intensity') else "強度不明"
                print(f"   - {interest.tag.name} ({level_text}, {intensity_text})")
        else:
            print("⚠️ ユーザーの興味関心が設定されていません")
        
        print("\n" + "=" * 80)
        
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
        
        print("\n🎯 === 推薦されたサークル（詳細分析） ===")
        for i, rec in enumerate(recommendations['recommendations'], 1):
            circle = rec['circle']
            score_breakdown = rec.get('score_breakdown', {})
            
            print(f"\n{i}. 【{circle.name}】")
            print(f"   🏆 総合スコア: {rec['score']:.3f}")
            print(f"   📈 信頼度: {rec['confidence']:.3f}")
            print(f"   👥 メンバー数: {circle.member_count}人")
            print(f"   📝 説明: {circle.description[:100]}...")
            
            if score_breakdown:
                total = score_breakdown.get('total', rec['score'])
                print(f"   --- 📊 スコア内訳 ---")
                hierarchical = score_breakdown.get('hierarchical', 0)
                collaborative = score_breakdown.get('collaborative', 0)
                behavioral = score_breakdown.get('behavioral', 0)
                diversity = score_breakdown.get('diversity', 0)
                popularity = score_breakdown.get('popularity', 0)
                
                print(f"   🎯 興味関心マッチ: {hierarchical:.3f} ({hierarchical/total*100:.1f}%)")
                print(f"   🤝 類似ユーザー: {collaborative:.3f} ({collaborative/total*100:.1f}%)")
                print(f"   📱 行動パターン: {behavioral:.3f} ({behavioral/total*100:.1f}%)")
                print(f"   🌈 多様性保証: {diversity:.3f} ({diversity/total*100:.1f}%)")
                print(f"   ⭐ 人気度ボーナス: {popularity:.3f} ({popularity/total*100:.1f}%)")
                
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
                
                print(f"   ✨ 主要因: {', '.join(main_contributors)}")
                
                # 一致度レベル判定
                match_level = "🔥 超高一致度" if total >= 0.9 else \
                             "🎯 高一致度" if total >= 0.7 else \
                             "📊 中一致度" if total >= 0.4 else \
                             "📝 低一致度"
                print(f"   {match_level} ({total:.1%})")
            
            # 推薦理由
            reasons = rec.get('reasons', [])
            if reasons:
                print(f"   --- 💭 推薦理由 ---")
                for j, reason in enumerate(reasons, 1):
                    print(f"   {j}. {reason['detail']}")
                    if reason.get('explanation'):
                        print(f"      💡 {reason['explanation']}")
        
        # 高一致度分析
        print("\n🔍 === 高一致度分析 ===")
        high_match_count = 0
        perfect_match_count = 0
        total_recommendations = len(recommendations['recommendations'])
        
        for rec in recommendations['recommendations']:
            score = rec['score']
            if score >= 0.9:
                perfect_match_count += 1
                print(f"🔥 [{rec['circle']['name']}] 完璧一致: {score:.1%}")
            elif score >= 0.7:
                high_match_count += 1
                print(f"🎯 [{rec['circle']['name']}] 高一致: {score:.1%}")
        
        print(f"\n📈 一致度分析結果:")
        print(f"🔥 完璧一致 (90%+): {perfect_match_count}/{total_recommendations}")
        print(f"🎯 高一致 (70%+): {high_match_count}/{total_recommendations}")
        print(f"📊 その他: {total_recommendations - perfect_match_count - high_match_count}/{total_recommendations}")
        
        if perfect_match_count > 0:
            print("🎉 完璧一致のサークルが見つかりました！")
        elif high_match_count > 0:
            print("✅ 高一致度のサークルが見つかりました！")
        else:
            print("💡 より高い一致度を得るには、興味関心の詳細登録をおすすめします")
        
    except User.DoesNotExist:
        print(f"❌ ユーザー '{username}' が見つかりませんでした")
        print("利用可能なテストユーザー:")
        users = User.objects.filter(username__in=['swift_expert', 'react_developer', 'music_lover', 'testuser'])
        for user in users:
            print(f"   - {user.username} ({user.display_name})")
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

def compare_multiple_users():
    """複数ユーザーの推薦結果を比較"""
    print("🔬 === 複数ユーザー比較分析 ===\n")
    
    test_users = ['swift_expert', 'react_developer', 'music_lover']
    results = {}
    
    for username in test_users:
        try:
            user = User.objects.get(username=username)
            engine = NextGenRecommendationEngine(user)
            recommendations = engine.generate_recommendations(algorithm='smart', limit=3)
            
            top_score = recommendations['recommendations'][0]['score'] if recommendations['recommendations'] else 0
            results[username] = {
                'user': user,
                'top_score': top_score,
                'total_recommendations': len(recommendations['recommendations'])
            }
            
        except User.DoesNotExist:
            continue
    
    # 結果を比較表示
    print("📊 ユーザー別最高スコア比較:")
    print("-" * 60)
    for username, data in sorted(results.items(), key=lambda x: x[1]['top_score'], reverse=True):
        user = data['user']
        score = data['top_score']
        match_level = "🔥 完璧一致" if score >= 0.9 else \
                     "🎯 高一致" if score >= 0.7 else \
                     "📊 中一致" if score >= 0.4 else \
                     "📝 低一致"
        
        print(f"{match_level} {user.display_name:25} {score:.1%}")

def main():
    """メイン実行関数"""
    import sys
    
    print("🚀 === 高一致度マッチングテスト ===\n")
    
    if len(sys.argv) > 1:
        # 特定ユーザーのテスト
        username = sys.argv[1]
        test_specific_user_recommendations(username)
    else:
        # 複数ユーザー比較
        compare_multiple_users()
        print("\n" + "="*60)
        print("💡 特定ユーザーの詳細分析を見るには:")
        print("   python test_high_match_recommendation.py swift_expert")
        print("   python test_high_match_recommendation.py react_developer")
        print("   python test_high_match_recommendation.py music_lover")

if __name__ == "__main__":
    main() 