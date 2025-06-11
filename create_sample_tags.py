#!/usr/bin/env python
import os
import sys
import django

# Djangoプロジェクトの設定
sys.path.append('/Users/t.i/develop/knest-app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'knest_backend.settings.base')
django.setup()

from knest_backend.apps.interests.models import Tag

# サンプルタグデータ
sample_tags = [
    "プログラミング", "Python", "JavaScript", "React", "Django",
    "機械学習", "AI", "データサイエンス", "ウェブ開発", "モバイル開発",
    "デザイン", "UI", "UX", "グラフィックデザイン", "フォトグラフィ",
    "読書", "小説", "ビジネス書", "自己啓発", "歴史",
    "映画", "アニメ", "音楽", "ゲーム", "アート",
    "スポーツ", "ランニング", "ヨガ", "筋トレ", "サッカー",
    "料理", "グルメ", "カフェ", "お酒", "コーヒー",
    "旅行", "温泉", "登山", "キャンプ", "写真",
    "英語", "中国語", "語学学習", "勉強", "資格",
    "起業", "副業", "投資", "経済", "マーケティング",
    "健康", "美容", "ダイエット", "マインドフルネス", "瞑想",
    "家族", "ペット", "犬", "猫", "ガーデニング"
]

def create_sample_tags():
    print("サンプルタグを作成しています...")
    
    created_count = 0
    for tag_name in sample_tags:
        tag, created = Tag.objects.get_or_create(
            name=tag_name,
            defaults={'usage_count': 0}
        )
        if created:
            created_count += 1
            print(f"✅ タグ作成: {tag_name}")
        else:
            print(f"⚠️ タグ既存: {tag_name}")
    
    print(f"\n🎉 {created_count}個の新しいタグを作成しました！")
    print(f"📊 合計タグ数: {Tag.objects.count()}個")

if __name__ == "__main__":
    create_sample_tags() 