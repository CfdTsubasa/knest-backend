#!/usr/bin/env python
"""興味関心データの確認スクリプト"""

import os
import sys
import django

# Djangoの設定
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'knest_backend.settings')
django.setup()

from knest_backend.apps.interests.models import Interest

def main():
    print("🎯 興味関心データ統計")
    print("=" * 50)
    
    total = Interest.objects.count()
    print(f"📊 合計興味関心数: {total}個")
    print()
    
    print("📋 カテゴリ別分布:")
    categories = [
        ('gaming', '🎮 ゲーム'),
        ('learning', '📚 学習・知識'),
        ('creative', '🎨 クリエイティブ'),
        ('sports', '🏃‍♂️ スポーツ'),
        ('food', '🍳 料理・グルメ'),
        ('travel', '🌍 旅行・アウトドア'),
        ('lifestyle', '💰 ライフスタイル'),
        ('entertainment', '🎭 エンターテイメント'),
        ('technical', '🔬 技術・専門'),
        ('business', '🎯 ビジネス・キャリア'),
        ('wellness', '🧠 自己開発・ウェルネス'),
    ]
    
    for cat_key, cat_name in categories:
        count = Interest.objects.filter(category=cat_key).count()
        print(f"  {cat_name}: {count}個")
    
    print()
    print("✅ シンプル選択システム準備完了！")
    print("✅ 5段階評価から選択/非選択方式に変更")
    print("✅ より多くの興味関心オプションを提供")

if __name__ == '__main__':
    main() 