#!/usr/bin/env python
"""
高い一致度マッチングのテスト用ダミーデータ作成スクリプト
完全一致（90%以上）から部分一致（30-50%）まで段階的に作成
"""
import os
import sys
import django
from datetime import date, timedelta
import random

# Django設定
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'knest_backend.settings.base')
django.setup()

from knest_backend.apps.users.models import User
from knest_backend.apps.circles.models import Circle
from knest_backend.apps.interests.models import InterestCategory, InterestSubcategory, InterestTag, UserInterestProfile

def create_perfect_match_scenario():
    """完全一致（90%以上）のシナリオを作成"""
    print("🔥 === 完全一致シナリオ作成中 ===")
    
    # Swift iOS開発完全一致ユーザー
    swift_user, created = User.objects.get_or_create(
        username='swift_expert',
        defaults={
            'email': 'swift.expert@example.com',
            'display_name': 'Swift専門家（完全一致テスト）',
            'birth_date': date(1990, 6, 15),
            'prefecture': 'tokyo'
        }
    )
    
    if created:
        swift_user.set_password('test123')
        swift_user.save()
        print(f"✅ Swift専門家ユーザー作成: {swift_user.display_name}")
    
    # Swift関連の詳細な興味関心を追加
    swift_interests = ['Swift', 'iOS開発', 'UIKit', 'SwiftUI', 'Xcode']
    
    for interest_name in swift_interests:
        try:
            tag = InterestTag.objects.filter(name=interest_name).first()
            if tag:
                UserInterestProfile.objects.get_or_create(
                    user=swift_user,
                    tag=tag,
                    defaults={'level': 3}  # 最高レベル
                )
                print(f"  ✅ 興味追加: {interest_name} (レベル3)")
            else:
                raise InterestTag.DoesNotExist
        except InterestTag.DoesNotExist:
            # タグが存在しない場合は作成
            tech_category = InterestCategory.objects.get(name='テクノロジー')
            mobile_subcategory = InterestSubcategory.objects.get(name='モバイル開発')
            new_tag = InterestTag.objects.create(
                subcategory=mobile_subcategory,
                name=interest_name,
                description=f"{interest_name}の開発技術"
            )
            UserInterestProfile.objects.create(
                user=swift_user,
                tag=new_tag,
                level=3
            )
            print(f"  🆕 新規タグ作成&追加: {interest_name}")
    
    # 完全一致するサークル作成
    swift_circle, created = Circle.objects.get_or_create(
        name='Swift & iOS開発サークル',
        defaults={
            'description': 'SwiftとiOS開発に特化した専門サークルです。UIKit、SwiftUI、Xcodeを使った実践的な開発を行います。',
            'member_count': 25,
            'tags': ['Swift', 'iOS開発', 'UIKit', 'SwiftUI', 'Xcode'],
            'creator_id': swift_user.id,
            'owner_id': swift_user.id
        }
    )
    
    if created:
        print(f"✅ Swift専門サークル作成: {swift_circle.name}")
        
        # サークルにタグを関連付け（InterestTagではなくInterestが必要）
        # for interest_name in swift_interests:
        #     tag = InterestTag.objects.filter(name=interest_name).first()
        #     if tag:
        #         swift_circle.interests.add(tag)
    
    return swift_user, swift_circle

def create_high_match_scenario():
    """高一致度（70-80%）のシナリオを作成"""
    print("🎯 === 高一致度シナリオ作成中 ===")
    
    # React開発者ユーザー
    react_user, created = User.objects.get_or_create(
        username='react_developer',
        defaults={
            'email': 'react.dev@example.com',
            'display_name': 'React開発者（高一致テスト）',
            'birth_date': date(1993, 9, 22),
            'prefecture': 'kanagawa'
        }
    )
    
    if created:
        react_user.set_password('test123')
        react_user.save()
        print(f"✅ React開発者ユーザー作成: {react_user.display_name}")
    
    # React + フロントエンド関連の興味
    react_interests = ['React', 'JavaScript', 'フロントエンド', 'UI/UXデザイン', 'TypeScript']
    
    for interest_name in react_interests:
        try:
            tag = InterestTag.objects.filter(name=interest_name).first()
            if tag:
                UserInterestProfile.objects.get_or_create(
                    user=react_user,
                    tag=tag,
                    defaults={'level': 2 if interest_name == 'UI/UXデザイン' else 3}
                )
                print(f"  ✅ 興味追加: {interest_name}")
            else:
                print(f"  ⚠️ タグが見つかりません: {interest_name}")
        except InterestTag.DoesNotExist:
            print(f"  ⚠️ タグが見つかりません: {interest_name}")
    
    # 部分一致するWeb開発サークル
    web_circle, created = Circle.objects.get_or_create(
        name='モダンWeb開発コミュニティ',
        defaults={
            'description': 'React、Vue.js、TypeScriptを使ったモダンなWeb開発を学ぶコミュニティです。',
            'member_count': 18,
            'tags': ['React', 'JavaScript', 'フロントエンド', 'TypeScript', 'Vue.js'],
            'creator_id': react_user.id,
            'owner_id': react_user.id
        }
    )
    
    if created:
        print(f"✅ Web開発サークル作成: {web_circle.name}")
    
    return react_user, web_circle

def create_medium_match_scenario():
    """中一致度（40-60%）のシナリオを作成"""
    print("📊 === 中一致度シナリオ作成中 ===")
    
    # 音楽好きユーザー
    music_user, created = User.objects.get_or_create(
        username='music_lover',
        defaults={
            'email': 'music.lover@example.com',
            'display_name': '音楽愛好家（中一致テスト）',
            'birth_date': date(1996, 2, 8),
            'prefecture': 'osaka'
        }
    )
    
    if created:
        music_user.set_password('test123')
        music_user.save()
        print(f"✅ 音楽愛好家ユーザー作成: {music_user.display_name}")
    
    # 音楽関連の興味
    music_interests = ['ギター', 'ピアノ', '作曲', 'ロック']
    
    for interest_name in music_interests:
        try:
            tag = InterestTag.objects.filter(name=interest_name).first()
            if tag:
                UserInterestProfile.objects.get_or_create(
                    user=music_user,
                    tag=tag,
                    defaults={'level': 2}
                )
                print(f"  ✅ 興味追加: {interest_name}")
            else:
                print(f"  ⚠️ タグが見つかりません: {interest_name}")
        except InterestTag.DoesNotExist:
            print(f"  ⚠️ タグが見つかりません: {interest_name}")
    
    # 関連するが少し違うアート系サークル
    creative_circle, created = Circle.objects.get_or_create(
        name='アート＆音楽クリエイター',
        defaults={
            'description': '音楽制作、イラスト、動画編集などクリエイティブな活動をするサークル',
            'member_count': 12,
            'tags': ['DTM', 'イラスト', '動画編集', '作曲', 'デザイン'],
            'creator_id': music_user.id,
            'owner_id': music_user.id
        }
    )
    
    if created:
        print(f"✅ クリエイターサークル作成: {creative_circle.name}")
    
    return music_user, creative_circle

def create_diverse_circles():
    """多様なテスト用サークルを作成"""
    print("🌈 === 多様なテストサークル作成中 ===")
    
    # 作成者として使用する既存ユーザーを取得
    creator_user = User.objects.first()
    if not creator_user:
        print("⚠️ 作成者ユーザーが見つかりません。スキップします。")
        return []
    
    test_circles = [
        {
            'name': 'AI・機械学習研究会',
            'description': 'Python、TensorFlow、機械学習アルゴリズムの研究開発',
            'member_count': 35,
            'tags': ['Python', '機械学習', 'AI', 'データサイエンス']
        },
        {
            'name': 'フットサル＆サッカー部',
            'description': '週末にフットサルやサッカーを楽しむスポーツサークル',
            'member_count': 22,
            'tags': ['サッカー', 'フットサル', '運動', 'チームスポーツ']
        },
        {
            'name': '英語conversation club',
            'description': 'ネイティブスピーカーとの英会話練習とTOEIC対策',
            'member_count': 15,
            'tags': ['英語', 'TOEIC', '国際交流', '語学']
        },
        {
            'name': 'ボードゲーム愛好会',
            'description': '戦略ゲーム、パーティゲームを楽しむコミュニティ',
            'member_count': 8,
            'tags': ['ボードゲーム', '戦略', '論理思考', '交流']
        }
    ]
    
    created_circles = []
    for circle_data in test_circles:
        circle, created = Circle.objects.get_or_create(
            name=circle_data['name'],
            defaults={
                'description': circle_data['description'],
                'member_count': circle_data['member_count'],
                'tags': circle_data['tags'],
                'creator': creator_user,
                'owner': creator_user
            }
        )
        
        if created:
            created_circles.append(circle)
            print(f"✅ サークル作成: {circle_data['name']}")
    
    return created_circles

def main():
    """メイン実行関数"""
    print("🚀 === 高一致度マッチングテスト用ダミーデータ作成開始 ===\n")
    
    try:
        # 1. 完全一致シナリオ
        swift_user, swift_circle = create_perfect_match_scenario()
        print()
        
        # 2. 高一致度シナリオ
        react_user, web_circle = create_high_match_scenario()
        print()
        
        # 3. 中一致度シナリオ
        music_user, creative_circle = create_medium_match_scenario()
        print()
        
        # 4. 多様なサークル
        diverse_circles = create_diverse_circles()
        print()
        
        print("🎉 === 高一致度テストデータ作成完了 ===")
        print("\n📋 作成されたテストユーザー:")
        print(f"   1. {swift_user.username} ({swift_user.display_name})")
        print(f"      - 完全一致期待: Swift & iOS開発サークル")
        print(f"   2. {react_user.username} ({react_user.display_name})")
        print(f"      - 高一致期待: モダンWeb開発コミュニティ")
        print(f"   3. {music_user.username} ({music_user.display_name})")
        print(f"      - 中一致期待: アート＆音楽クリエイター")
        
        print("\n🔬 次のステップ:")
        print("   python test_recommendation.py を実行して推薦結果を確認してください")
        print("   特に swift_expert ユーザーで90%以上の高スコアが期待されます！")
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 