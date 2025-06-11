#!/usr/bin/env python
"""
3階層興味関心システムの初期サンプルデータを作成するスクリプト
"""

import os
import django
import sys
from datetime import date, timedelta
import random

# Django環境設定
sys.path.append('/Users/t.i/develop/knest-app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'knest_backend.settings.base')
django.setup()

from knest_backend.apps.interests.models import InterestCategory, InterestSubcategory, InterestTag, UserInterestProfile
from knest_backend.apps.users.models import User

def create_hierarchical_interest_data():
    """3階層興味関心システムのサンプルデータを作成"""
    
    print("🚀 3階層興味関心システムのサンプルデータを作成中...")
    
    # カテゴリ、サブカテゴリ、タグの構造定義
    hierarchy_data = {
        "テクノロジー": {
            "type": "technical",
            "description": "プログラミング、IT関連の技術分野",
            "icon_url": "https://example.com/icons/technology.png",
            "subcategories": {
                "プログラミング": {
                    "description": "各種プログラミング言語・フレームワーク",
                    "tags": [
                        {"name": "Python", "description": "Python言語でのプログラミング"},
                        {"name": "JavaScript", "description": "JavaScript開発"},
                        {"name": "Swift", "description": "iOS・macOSアプリ開発"},
                        {"name": "React", "description": "Reactを使ったフロントエンド開発"},
                        {"name": "Django", "description": "Djangoを使ったWebアプリ開発"},
                        {"name": "機械学習", "description": "AI・機械学習の実装"}
                    ]
                },
                "モバイル開発": {
                    "description": "スマートフォンアプリの開発",
                    "tags": [
                        {"name": "iOS開発", "description": "iPhoneアプリ開発"},
                        {"name": "Android開発", "description": "Androidアプリ開発"},
                        {"name": "Flutter", "description": "クロスプラットフォーム開発"},
                        {"name": "React Native", "description": "React Nativeでのアプリ開発"}
                    ]
                },
                "Web開発": {
                    "description": "Webサイト・Webアプリケーションの開発",
                    "tags": [
                        {"name": "フロントエンド", "description": "UI/UX実装"},
                        {"name": "バックエンド", "description": "サーバーサイド開発"},
                        {"name": "フルスタック", "description": "全体的な開発"},
                        {"name": "API開発", "description": "WebAPI設計・実装"}
                    ]
                }
            }
        },
        "アート・クリエイティブ": {
            "type": "creative",
            "description": "芸術・デザイン・創作活動",
            "icon_url": "https://example.com/icons/art.png",
            "subcategories": {
                "デザイン": {
                    "description": "グラフィック・UI/UXデザイン",
                    "tags": [
                        {"name": "UI/UXデザイン", "description": "ユーザーインターフェース設計"},
                        {"name": "グラフィックデザイン", "description": "ビジュアルデザイン"},
                        {"name": "ロゴデザイン", "description": "ブランドロゴ作成"},
                        {"name": "イラスト", "description": "デジタル・アナログイラスト"}
                    ]
                },
                "音楽": {
                    "description": "音楽制作・演奏",
                    "tags": [
                        {"name": "作曲", "description": "楽曲制作"},
                        {"name": "ギター", "description": "ギター演奏"},
                        {"name": "ピアノ", "description": "ピアノ演奏"},
                        {"name": "DTM", "description": "デジタル音楽制作"}
                    ]
                },
                "映像制作": {
                    "description": "動画・映像の企画・制作",
                    "tags": [
                        {"name": "動画編集", "description": "映像編集・加工"},
                        {"name": "映画制作", "description": "ショートフィルム・映画制作"},
                        {"name": "YouTube", "description": "YouTube動画制作"},
                        {"name": "アニメーション", "description": "2D/3Dアニメーション制作"}
                    ]
                }
            }
        },
        "スポーツ・健康": {
            "type": "sports",
            "description": "運動・スポーツ・健康管理",
            "icon_url": "https://example.com/icons/sports.png",
            "subcategories": {
                "球技スポーツ": {
                    "description": "ボールを使ったスポーツ",
                    "tags": [
                        {"name": "サッカー", "description": "サッカー・フットサル"},
                        {"name": "バスケットボール", "description": "バスケ・ストリートボール"},
                        {"name": "テニス", "description": "硬式・軟式テニス"},
                        {"name": "野球", "description": "野球・ソフトボール"}
                    ]
                },
                "フィットネス": {
                    "description": "筋トレ・体力づくり",
                    "tags": [
                        {"name": "筋力トレーニング", "description": "ウエイトトレーニング"},
                        {"name": "ランニング", "description": "ジョギング・マラソン"},
                        {"name": "ヨガ", "description": "ヨガ・ピラティス"},
                        {"name": "水泳", "description": "競泳・水中エクササイズ"}
                    ]
                },
                "アウトドア": {
                    "description": "屋外でのスポーツ・活動",
                    "tags": [
                        {"name": "ハイキング", "description": "山歩き・トレッキング"},
                        {"name": "キャンプ", "description": "アウトドアキャンプ"},
                        {"name": "サイクリング", "description": "自転車・ロードバイク"},
                        {"name": "クライミング", "description": "ボルダリング・ロッククライミング"}
                    ]
                }
            }
        },
        "学習・知識": {
            "type": "learning",
            "description": "学問・資格・スキルアップ",
            "icon_url": "https://example.com/icons/learning.png",
            "subcategories": {
                "語学": {
                    "description": "外国語学習",
                    "tags": [
                        {"name": "英語", "description": "英語学習・TOEIC対策"},
                        {"name": "中国語", "description": "中国語学習"},
                        {"name": "韓国語", "description": "韓国語学習"},
                        {"name": "日本語", "description": "日本語学習（外国人向け）"}
                    ]
                },
                "資格取得": {
                    "description": "各種資格・検定の取得",
                    "tags": [
                        {"name": "IT資格", "description": "ITパスポート・基本情報技術者"},
                        {"name": "簿記", "description": "日商簿記検定"},
                        {"name": "宅建", "description": "宅地建物取引士"},
                        {"name": "FP", "description": "ファイナンシャルプランナー"}
                    ]
                },
                "学術研究": {
                    "description": "学問・研究活動",
                    "tags": [
                        {"name": "心理学", "description": "心理学研究・学習"},
                        {"name": "哲学", "description": "哲学・思想研究"},
                        {"name": "歴史", "description": "歴史研究・史跡巡り"},
                        {"name": "科学", "description": "自然科学・実験"}
                    ]
                }
            }
        }
    }
    
    # データベースに挿入
    created_counts = {"categories": 0, "subcategories": 0, "tags": 0}
    
    for category_name, category_data in hierarchy_data.items():
        # カテゴリ作成
        category, created = InterestCategory.objects.get_or_create(
            name=category_name,
            defaults={
                "type": category_data["type"],
                "description": category_data["description"],
                "icon_url": category_data.get("icon_url")
            }
        )
        if created:
            created_counts["categories"] += 1
            print(f"✅ カテゴリ作成: {category_name}")
        
        # サブカテゴリ作成
        for subcategory_name, subcategory_data in category_data["subcategories"].items():
            subcategory, created = InterestSubcategory.objects.get_or_create(
                category=category,
                name=subcategory_name,
                defaults={
                    "description": subcategory_data["description"]
                }
            )
            if created:
                created_counts["subcategories"] += 1
                print(f"  ✅ サブカテゴリ作成: {subcategory_name}")
            
            # タグ作成
            for tag_data in subcategory_data["tags"]:
                tag, created = InterestTag.objects.get_or_create(
                    subcategory=subcategory,
                    name=tag_data["name"],
                    defaults={
                        "description": tag_data["description"],
                        "usage_count": random.randint(1, 50)
                    }
                )
                if created:
                    created_counts["tags"] += 1
                    print(f"    ✅ タグ作成: {tag_data['name']}")
    
    print(f"\n📊 作成完了!")
    print(f"   - カテゴリ: {created_counts['categories']}個")
    print(f"   - サブカテゴリ: {created_counts['subcategories']}個")
    print(f"   - タグ: {created_counts['tags']}個")
    
    return created_counts

def create_sample_user_profiles():
    """サンプルユーザーの興味関心プロフィールを作成"""
    
    print("\n🧪 サンプルユーザーの興味関心プロフィールを作成中...")
    
    # testuserを取得または作成
    test_user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com',
            'display_name': 'テストユーザー',
            'birth_date': date(1995, 5, 15),
            'prefecture': 'tokyo'
        }
    )
    
    if created:
        test_user.set_password('testpass123')
        test_user.save()
        print(f"✅ testuserを作成しました")
    else:
        # 既存ユーザーのプロフィール更新
        test_user.birth_date = date(1995, 5, 15)
        test_user.prefecture = 'tokyo'
        test_user.save()
        print(f"✅ testuserのプロフィールを更新しました")
    
    # ランダムなタグを選択してユーザープロフィールを作成
    all_tags = list(InterestTag.objects.all())
    if all_tags:
        selected_tags = random.sample(all_tags, min(8, len(all_tags)))
        
        for tag in selected_tags:
            profile, created = UserInterestProfile.objects.get_or_create(
                user=test_user,
                tag=tag,
                defaults={
                    'intensity': random.randint(3, 5)
                }
            )
            if created:
                print(f"  ✅ 興味追加: {tag.name} (強度: {profile.intensity})")
    
    # 追加のサンプルユーザー作成
    sample_users = [
        {
            'username': 'developer_alice',
            'email': 'alice@example.com',
            'display_name': 'アリス（開発者）',
            'birth_date': date(1992, 8, 20),
            'prefecture': 'tokyo',
            'interests': ['Python', 'React', 'UI/UXデザイン', 'ランニング']
        },
        {
            'username': 'designer_bob',
            'email': 'bob@example.com',
            'display_name': 'ボブ（デザイナー）',
            'birth_date': date(1990, 3, 10),
            'prefecture': 'osaka',
            'interests': ['グラフィックデザイン', 'イラスト', 'DTM', 'ヨガ']
        },
        {
            'username': 'student_charlie',
            'email': 'charlie@example.com',
            'display_name': 'チャーリー（学生）',
            'birth_date': date(1998, 12, 5),
            'prefecture': 'kanagawa',
            'interests': ['英語', 'バスケットボール', 'YouTube', '心理学']
        }
    ]
    
    for user_data in sample_users:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'email': user_data['email'],
                'display_name': user_data['display_name'],
                'birth_date': user_data['birth_date'],
                'prefecture': user_data['prefecture']
            }
        )
        
        if created:
            user.set_password('password123')
            user.save()
            print(f"✅ サンプルユーザー作成: {user_data['display_name']}")
            
            # 興味関心を追加
            for interest_name in user_data['interests']:
                try:
                    tag = InterestTag.objects.get(name=interest_name)
                    UserInterestProfile.objects.get_or_create(
                        user=user,
                        tag=tag,
                        defaults={'intensity': random.randint(3, 5)}
                    )
                except InterestTag.DoesNotExist:
                    print(f"  ⚠️ タグが見つかりません: {interest_name}")
    
    print(f"\n✅ サンプルユーザープロフィール作成完了!")

if __name__ == "__main__":
    try:
        # 3階層データ作成
        create_hierarchical_interest_data()
        
        # サンプルユーザープロフィール作成
        create_sample_user_profiles()
        
        print(f"\n🎉 3階層興味関心システムのサンプルデータ作成が完了しました！")
        print(f"")
        print(f"📍 確認方法:")
        print(f"   - Django Admin: http://localhost:8000/admin/")
        print(f"   - API: http://localhost:8000/api/interests/hierarchical/tree/")
        print(f"   - マッチング: http://localhost:8000/api/interests/matching/find_user_matches/")
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc() 