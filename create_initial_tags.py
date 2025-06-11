#!/usr/bin/env python
"""
初期ハッシュタグデータ作成スクリプト
"""

import os
import sys
import django

# Django設定
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'knest_backend.settings')
django.setup()

from knest_backend.apps.interests.models import Tag

def create_initial_tags():
    """人気のハッシュタグを初期データとして作成"""
    
    initial_tags = [
        # プログラミング・技術
        'プログラミング', 'python', 'javascript', 'react', 'ios開発',
        'web開発', 'ai', '機械学習', 'データサイエンス', 'ui_ux',
        
        # ゲーム
        'ゲーム', 'fps', 'rpg', 'インディーゲーム', 'eスポーツ',
        'ゲーム開発', 'unity', 'switch', 'ps5', 'pcゲーム',
        
        # 創作・デザイン
        'デザイン', 'イラスト', '写真', '動画編集', '音楽',
        'dtm', '3dcg', 'アニメ', '漫画', 'ハンドメイド',
        
        # 学習・読書
        '読書', '英語学習', '資格取得', 'toeic', '大学受験',
        '語学', '哲学', '心理学', '歴史', '科学',
        
        # スポーツ・健康
         'ランニング', 'ジム', 'ヨガ', 'サッカー', 'バスケ',
        'テニス', '筋トレ', 'ダイエット', 'マラソン', '登山',
        
        # ビジネス・起業
        '起業', 'スタートアップ', 'マーケティング', '投資',
        'フリーランス', '副業', 'ビジネス', 'セールス', 'コンサル',
        
        # エンターテイメント
        '映画', 'アニメ', 'ドラマ', '音楽鑑賞', 'ライブ',
        'コンサート', '舞台', 'お笑い', 'カラオケ', 'ダンス',
        
        # 趣味・ライフスタイル
        '料理', 'カフェ', '旅行', 'キャンプ', 'diy',
        'ガーデニング', 'ペット', '猫', '犬', 'カメラ',
    ]
    
    created_count = 0
    
    for tag_name in initial_tags:
        tag, created = Tag.objects.get_or_create(
            name=tag_name,
            defaults={'usage_count': 0}
        )
        
        if created:
            created_count += 1
            print(f"✅ 作成: #{tag_name}")
        else:
            print(f"⚠️ 既存: #{tag_name}")
    
    print(f"\n🎉 完了！ {created_count}個の新規タグを作成しました。")
    print(f"📊 総タグ数: {Tag.objects.count()}")

if __name__ == "__main__":
    create_initial_tags() 