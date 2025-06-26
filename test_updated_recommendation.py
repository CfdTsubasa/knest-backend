#!/usr/bin/env python
"""
推薦システムの重み調整テスト
興味関心の寄与率向上を確認
"""
import os
import django

# Django設定
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'knest_backend.settings')
django.setup()

from knest_backend.apps.users.models import User
from knest_backend.apps.recommendations.engines import NextGenRecommendationEngine
import logging

# ログレベルを設定
logging.basicConfig(level=logging.INFO)

def test_updated_weights():
    """更新された重みシステムのテスト"""
    
    print("🔬 興味関心重み調整テスト開始")
    print("=" * 50)
    
    # testuser6363で推薦テスト
    user = User.objects.get(username='testuser6363')
    engine = NextGenRecommendationEngine(user)
    
    # 新しい重み確認
    weights = engine.calculate_algorithm_weights()
    print('📊 新しいアルゴリズム重み:')
    for key, value in weights.items():
        if key == 'hierarchical':
            print(f'  ✅ {key}: {value:.1%} (興味関心 - 大幅強化!)')
        else:
            print(f'  📉 {key}: {value:.1%}')
    
    print(f"\n🎯 興味関心の重み: {weights['hierarchical']:.1%}")
    print(f"   従来: 40-60% → 新規: {weights['hierarchical']:.1%} (+{(weights['hierarchical']-0.4)*100:.0f}%)")
    
    # 推薦生成
    print("\n🚀 推薦生成中...")
    result = engine.generate_recommendations(limit=3)
    
    print(f"\n✅ 推薦結果: {len(result['recommendations'])}件")
    print("=" * 50)
    
    # 興味関心寄与率の分析
    total_interest_contribution = 0
    total_recommendations = len(result['recommendations'])
    
    for i, rec in enumerate(result['recommendations'], 1):
        breakdown = rec['score_breakdown']
        total = breakdown['total']
        hierarchical_score = breakdown['hierarchical']
        hierarchical_pct = (hierarchical_score / total * 100) if total > 0 else 0
        
        total_interest_contribution += hierarchical_pct
        
        print(f"{i}. 【{rec['circle'].name}】 総合スコア: {total:.3f}")
        print(f"   🎯 階層マッチング: {hierarchical_score:.3f} ({hierarchical_pct:.1f}%)")
        print(f"   🤝 協調フィルタリング: {breakdown['collaborative']:.3f} ({breakdown['collaborative']/total*100:.1f}%)")
        print(f"   📈 行動ベース: {breakdown['behavioral']:.3f} ({breakdown['behavioral']/total*100:.1f}%)")
        print(f"   🌟 人気度ボーナス: {breakdown['popularity']:.3f} ({breakdown['popularity']/total*100:.1f}%)")
        print(f"   🎨 多様性保証: {breakdown['diversity']:.3f} ({breakdown['diversity']/total*100:.1f}%)")
        
        if hierarchical_pct >= 70:
            print(f"   ✅ 興味関心主導の推薦！")
        elif hierarchical_pct >= 50:
            print(f"   ⚖️ 興味関心重視の推薦")
        else:
            print(f"   ⚠️ 興味関心の寄与が低い")
        print()
    
    # 統計
    avg_interest_contribution = total_interest_contribution / total_recommendations if total_recommendations > 0 else 0
    
    print("📈 分析結果:")
    print(f"   平均興味関心寄与率: {avg_interest_contribution:.1f}%")
    
    if avg_interest_contribution >= 70:
        print(f"   🎉 大成功！興味関心が推薦の主要因になっています")
    elif avg_interest_contribution >= 60:
        print(f"   ✅ 成功！興味関心の影響力が大幅に向上しました")
    elif avg_interest_contribution >= 50:
        print(f"   📈 改善！興味関心の寄与率が向上しています")
    else:
        print(f"   ⚠️ さらなる調整が必要です")
    
    # 推薦理由の確認
    print(f"\n💬 推薦理由（最初の推薦）:")
    if result['recommendations']:
        reasons = result['recommendations'][0]['reasons']
        for reason in reasons:
            print(f"   • {reason}")
    
    print("=" * 50)
    print("🏁 テスト完了")

if __name__ == "__main__":
    test_updated_weights() 