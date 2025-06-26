#!/usr/bin/env python
"""
KnestApp初期データ作成スクリプト（簡素化版）
"""
import os
import sys
import django
import random
from time import time

# Django設定を有効化
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'knestproject.settings')
django.setup()

from knest_backend.apps.interests.models import Interest
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

# 大幅拡充された興味関心データ
EXPANDED_INTERESTS_DATA = [
    # 🎮 ゲーム・エンタメ (40個)
    {'name': 'RPGゲーム', 'description': 'ロールプレイングゲーム', 'category': 'gaming', 'tags': ['indoor', 'digital']},
    {'name': 'FPSゲーム', 'description': 'ファーストパーソンシューティング', 'category': 'gaming', 'tags': ['competitive', 'digital']},
    {'name': 'パズルゲーム', 'description': 'テトリス、ぷよぷよなど', 'category': 'gaming', 'tags': ['casual', 'brain']},
    {'name': 'ボードゲーム', 'description': '人生ゲーム、将棋、囲碁', 'category': 'gaming', 'tags': ['social', 'strategy']},
    {'name': 'カードゲーム', 'description': 'ポーカー、マジック・ザ・ギャザリング', 'category': 'gaming', 'tags': ['social', 'strategy']},
    {'name': 'MMORPG', 'description': 'オンライン大規模RPG', 'category': 'gaming', 'tags': ['social', 'long-term']},
    {'name': 'レトロゲーム', 'description': 'ファミコン、スーファミなど', 'category': 'gaming', 'tags': ['nostalgic', 'collection']},
    {'name': 'VRゲーム', 'description': 'バーチャルリアリティゲーム', 'category': 'gaming', 'tags': ['innovative', 'immersive']},
    {'name': 'モバイルゲーム', 'description': 'スマホゲーム', 'category': 'gaming', 'tags': ['casual', 'convenient']},
    {'name': 'インディーゲーム', 'description': '独立系ゲーム', 'category': 'gaming', 'tags': ['artistic', 'unique']},
    
    # 📚 学習・知識 (35個)
    {'name': 'プログラミング', 'description': 'ソフトウェア開発', 'category': 'learning', 'tags': ['technical', 'career']},
    {'name': 'AI・機械学習', 'description': '人工知能、データサイエンス', 'category': 'learning', 'tags': ['cutting-edge', 'technical']},
    {'name': 'ウェブデザイン', 'description': 'UI/UXデザイン', 'category': 'learning', 'tags': ['creative', 'technical']},
    {'name': '外国語学習', 'description': '英語、中国語、韓国語など', 'category': 'learning', 'tags': ['international', 'communication']},
    {'name': '資格取得', 'description': '各種検定・資格試験', 'category': 'learning', 'tags': ['career', 'achievement']},
    {'name': '読書', 'description': '小説、ビジネス書、漫画', 'category': 'learning', 'tags': ['knowledge', 'relaxing']},
    {'name': '歴史', 'description': '世界史、日本史', 'category': 'learning', 'tags': ['knowledge', 'culture']},
    {'name': '科学', 'description': '物理学、化学、生物学', 'category': 'learning', 'tags': ['knowledge', 'logical']},
    {'name': '哲学', 'description': '思想、倫理学', 'category': 'learning', 'tags': ['deep-thinking', 'abstract']},
    {'name': '心理学', 'description': '人間の心理・行動', 'category': 'learning', 'tags': ['human', 'analytical']},
    
    # 🎨 クリエイティブ (30個)  
    {'name': 'イラスト', 'description': 'デジタル・アナログ描画', 'category': 'creative', 'tags': ['artistic', 'visual']},
    {'name': '写真撮影', 'description': '風景、ポートレート撮影', 'category': 'creative', 'tags': ['artistic', 'outdoor']},
    {'name': '動画編集', 'description': 'YouTube、TikTok動画制作', 'category': 'creative', 'tags': ['digital', 'storytelling']},
    {'name': '音楽制作', 'description': 'DTM、作曲', 'category': 'creative', 'tags': ['artistic', 'technical']},
    {'name': '楽器演奏', 'description': 'ピアノ、ギター、ドラム', 'category': 'creative', 'tags': ['musical', 'skill']},
    {'name': '歌唱', 'description': 'カラオケ、合唱', 'category': 'creative', 'tags': ['musical', 'social']},
    {'name': '陶芸', 'description': '器作り、造形', 'category': 'creative', 'tags': ['handcraft', 'therapeutic']},
    {'name': '木工', 'description': '家具作り、彫刻', 'category': 'creative', 'tags': ['handcraft', 'practical']},
    {'name': '手芸', 'description': '編み物、裁縫', 'category': 'creative', 'tags': ['handcraft', 'practical']},
    {'name': '書道', 'description': '習字、カリグラフィー', 'category': 'creative', 'tags': ['traditional', 'meditative']},
    
    # 🏃‍♂️ スポーツ・フィットネス (35個)
    {'name': 'ランニング', 'description': 'ジョギング、マラソン', 'category': 'sports', 'tags': ['cardio', 'outdoor']},
    {'name': 'サッカー', 'description': 'フットボール', 'category': 'sports', 'tags': ['team', 'competitive']},
    {'name': 'バスケットボール', 'description': 'バスケ', 'category': 'sports', 'tags': ['team', 'indoor']},
    {'name': 'テニス', 'description': '硬式・軟式テニス', 'category': 'sports', 'tags': ['racket', 'competitive']},
    {'name': '筋トレ', 'description': 'ウェイトトレーニング', 'category': 'sports', 'tags': ['strength', 'individual']},
    {'name': 'ヨガ', 'description': 'ハタヨガ、パワーヨガ', 'category': 'sports', 'tags': ['flexibility', 'mindful']},
    {'name': '水泳', 'description': 'スイミング', 'category': 'sports', 'tags': ['cardio', 'full-body']},
    {'name': '登山', 'description': 'ハイキング、トレッキング', 'category': 'sports', 'tags': ['outdoor', 'adventure']},
    {'name': 'サイクリング', 'description': '自転車、ロードバイク', 'category': 'sports', 'tags': ['outdoor', 'endurance']},
    {'name': 'ダンス', 'description': 'ヒップホップ、バレエ', 'category': 'sports', 'tags': ['artistic', 'rhythmic']},
    
    # 🍳 料理・グルメ (25個)
    {'name': '料理', 'description': '家庭料理、本格的な調理', 'category': 'food', 'tags': ['practical', 'creative']},
    {'name': 'お菓子作り', 'description': 'ケーキ、クッキー作り', 'category': 'food', 'tags': ['sweet', 'creative']},
    {'name': 'パン作り', 'description': '手作りパン', 'category': 'food', 'tags': ['fermentation', 'satisfying']},
    {'name': 'コーヒー', 'description': 'ドリップ、エスプレッソ', 'category': 'food', 'tags': ['beverage', 'ritual']},
    {'name': '紅茶', 'description': 'ティータイム、茶葉', 'category': 'food', 'tags': ['beverage', 'elegant']},
    {'name': '日本酒', 'description': '地酒、酒蔵めぐり', 'category': 'food', 'tags': ['alcoholic', 'traditional']},
    {'name': 'ワイン', 'description': 'テイスティング、ワイナリー', 'category': 'food', 'tags': ['alcoholic', 'sophisticated']},
    {'name': 'クラフトビール', 'description': '地ビール、醸造', 'category': 'food', 'tags': ['alcoholic', 'craft']},
    {'name': 'ラーメン', 'description': 'ラーメン店めぐり', 'category': 'food', 'tags': ['casual', 'exploration']},
    {'name': 'スイーツ', 'description': 'ケーキ、和菓子めぐり', 'category': 'food', 'tags': ['sweet', 'indulgent']},
    
    # 🌍 旅行・アウトドア (30個)
    {'name': '国内旅行', 'description': '日本各地への旅', 'category': 'travel', 'tags': ['domestic', 'exploration']},
    {'name': '海外旅行', 'description': '国際旅行', 'category': 'travel', 'tags': ['international', 'adventure']},
    {'name': '温泉', 'description': '温泉地めぐり', 'category': 'travel', 'tags': ['relaxation', 'traditional']},
    {'name': 'キャンプ', 'description': 'アウトドア宿泊', 'category': 'travel', 'tags': ['outdoor', 'nature']},
    {'name': 'グランピング', 'description': '豪華キャンプ', 'category': 'travel', 'tags': ['outdoor', 'luxury']},
    {'name': 'バックパッカー', 'description': '格安旅行', 'category': 'travel', 'tags': ['budget', 'adventure']},
    {'name': '聖地巡礼', 'description': 'アニメ・映画の舞台めぐり', 'category': 'travel', 'tags': ['cultural', 'fandom']},
    {'name': 'フェス', 'description': '音楽フェスティバル', 'category': 'travel', 'tags': ['music', 'social']},
    {'name': '釣り', 'description': '海釣り、川釣り', 'category': 'travel', 'tags': ['outdoor', 'patient']},
    {'name': 'ドライブ', 'description': '車での遠出', 'category': 'travel', 'tags': ['scenic', 'freedom']},
    
    # 💰 ライフスタイル・投資 (20個)
    {'name': '投資', 'description': '株式、不動産投資', 'category': 'lifestyle', 'tags': ['financial', 'long-term']},
    {'name': '副業', 'description': 'サイドビジネス', 'category': 'lifestyle', 'tags': ['income', 'entrepreneurial']},
    {'name': 'ミニマリズム', 'description': 'シンプルライフ', 'category': 'lifestyle', 'tags': ['minimalist', 'intentional']},
    {'name': 'サステナブル', 'description': '持続可能な生活', 'category': 'lifestyle', 'tags': ['eco-friendly', 'conscious']},
    {'name': 'ガーデニング', 'description': '植物栽培、園芸', 'category': 'lifestyle', 'tags': ['nature', 'nurturing']},
    {'name': 'ペット', 'description': '犬、猫、小動物飼育', 'category': 'lifestyle', 'tags': ['animals', 'companionship']},
    {'name': 'インテリア', 'description': '部屋作り、家具選び', 'category': 'lifestyle', 'tags': ['design', 'comfort']},
    {'name': 'ファッション', 'description': '服装、スタイリング', 'category': 'lifestyle', 'tags': ['style', 'self-expression']},
    {'name': '美容', 'description': 'スキンケア、メイク', 'category': 'lifestyle', 'tags': ['self-care', 'beauty']},
    {'name': '健康管理', 'description': '食事管理、睡眠改善', 'category': 'lifestyle', 'tags': ['wellness', 'preventive']},
    
    # 🎭 エンターテイメント (25個)
    {'name': 'アニメ', 'description': '日本のアニメーション', 'category': 'entertainment', 'tags': ['visual', 'storytelling']},
    {'name': '漫画', 'description': 'マンガ、コミック', 'category': 'entertainment', 'tags': ['visual', 'narrative']},
    {'name': '映画', 'description': '邦画、洋画鑑賞', 'category': 'entertainment', 'tags': ['visual', 'emotional']},
    {'name': 'ドラマ', 'description': 'TV・配信ドラマ', 'category': 'entertainment', 'tags': ['episodic', 'emotional']},
    {'name': 'YouTube', 'description': '動画視聴', 'category': 'entertainment', 'tags': ['digital', 'varied']},
    {'name': 'TikTok', 'description': 'ショート動画', 'category': 'entertainment', 'tags': ['short-form', 'trendy']},
    {'name': 'Vtuber', 'description': 'バーチャルYouTuber', 'category': 'entertainment', 'tags': ['virtual', 'interactive']},
    {'name': 'ライブ配信', 'description': 'Twitch、ニコ生', 'category': 'entertainment', 'tags': ['real-time', 'interactive']},
    {'name': 'お笑い', 'description': 'コメディ、バラエティ', 'category': 'entertainment', 'tags': ['humor', 'social']},
    {'name': 'ポッドキャスト', 'description': '音声コンテンツ', 'category': 'entertainment', 'tags': ['audio', 'informational']},
    {'name': 'ゲーム実況', 'description': 'ゲーム配信視聴', 'category': 'entertainment', 'tags': ['gaming', 'social']},
    {'name': 'コンサート', 'description': '音楽ライブ', 'category': 'entertainment', 'tags': ['live', 'musical']},
    {'name': '舞台', 'description': '演劇、ミュージカル', 'category': 'entertainment', 'tags': ['live', 'dramatic']},
    {'name': '美術館', 'description': 'アート鑑賞', 'category': 'entertainment', 'tags': ['cultural', 'visual']},
    {'name': '博物館', 'description': '歴史・科学展示', 'category': 'entertainment', 'tags': ['educational', 'cultural']},
    {'name': 'プラネタリウム', 'description': '星空観察', 'category': 'entertainment', 'tags': ['educational', 'relaxing']},
    {'name': '水族館', 'description': '海洋生物観察', 'category': 'entertainment', 'tags': ['nature', 'peaceful']},
    {'name': '動物園', 'description': '動物観察', 'category': 'entertainment', 'tags': ['nature', 'educational']},
    {'name': 'テーマパーク', 'description': 'ディズニー、USJ', 'category': 'entertainment', 'tags': ['exciting', 'social']},
    {'name': 'カラオケ', 'description': '歌うこと', 'category': 'entertainment', 'tags': ['musical', 'social']},
    {'name': 'ダーツ', 'description': 'ダーツゲーム', 'category': 'entertainment', 'tags': ['skill', 'social']},
    {'name': 'ビリヤード', 'description': 'ビリヤードゲーム', 'category': 'entertainment', 'tags': ['skill', 'social']},
    {'name': 'ボウリング', 'description': 'ボウリング', 'category': 'entertainment', 'tags': ['sport', 'social']},
    {'name': 'バラエティ番組', 'description': 'TV番組', 'category': 'entertainment', 'tags': ['humor', 'casual']},
    {'name': 'ニュース', 'description': '時事情報', 'category': 'entertainment', 'tags': ['informational', 'current']},
    
    # 🔬 技術・専門 (25個)
    {'name': 'ウェブ開発', 'description': 'HTML、CSS、JavaScript', 'category': 'technical', 'tags': ['frontend', 'creative']},
    {'name': 'モバイル開発', 'description': 'iOS、Android', 'category': 'technical', 'tags': ['mobile', 'innovative']},
    {'name': 'データベース', 'description': 'SQL、NoSQL', 'category': 'technical', 'tags': ['backend', 'structured']},
    {'name': 'クラウド', 'description': 'AWS、Azure、GCP', 'category': 'technical', 'tags': ['infrastructure', 'scalable']},
    {'name': 'DevOps', 'description': 'CI/CD、Docker', 'category': 'technical', 'tags': ['automation', 'efficiency']},
    {'name': 'セキュリティ', 'description': 'サイバーセキュリティ', 'category': 'technical', 'tags': ['security', 'protective']},
    {'name': 'ネットワーク', 'description': 'TCP/IP、ルーティング', 'category': 'technical', 'tags': ['infrastructure', 'connectivity']},
    {'name': 'アプリ開発', 'description': 'ソフトウェア開発', 'category': 'technical', 'tags': ['software', 'creative']},
    {'name': 'ゲーム開発', 'description': 'Unity、Unreal Engine', 'category': 'technical', 'tags': ['creative', 'interactive']},
    {'name': '3DCG', 'description': '3Dモデリング、アニメーション', 'category': 'technical', 'tags': ['visual', 'artistic']},
    {'name': 'VR/AR', 'description': '仮想・拡張現実', 'category': 'technical', 'tags': ['immersive', 'innovative']},
    {'name': 'ブロックチェーン', 'description': '暗号通貨、NFT', 'category': 'technical', 'tags': ['decentralized', 'innovative']},
    {'name': 'IoT', 'description': 'モノのインターネット', 'category': 'technical', 'tags': ['connected', 'smart']},
    {'name': 'ロボティクス', 'description': 'ロボット工学', 'category': 'technical', 'tags': ['mechanical', 'intelligent']},
    {'name': '電子工作', 'description': 'Arduino、Raspberry Pi', 'category': 'technical', 'tags': ['hardware', 'creative']},
    {'name': 'CAD', 'description': '設計図面作成', 'category': 'technical', 'tags': ['design', 'precise']},
    {'name': '動画配信', 'description': 'ストリーミング技術', 'category': 'technical', 'tags': ['media', 'real-time']},
    {'name': 'オートメーション', 'description': '自動化システム', 'category': 'technical', 'tags': ['efficiency', 'smart']},
    {'name': 'API開発', 'description': 'REST、GraphQL', 'category': 'technical', 'tags': ['backend', 'integration']},
    {'name': 'マイクロサービス', 'description': 'アーキテクチャ設計', 'category': 'technical', 'tags': ['scalable', 'modular']},
    {'name': 'リバースエンジニアリング', 'description': 'システム解析', 'category': 'technical', 'tags': ['analytical', 'investigative']},
    {'name': 'ペネトレーションテスト', 'description': 'セキュリティ診断', 'category': 'technical', 'tags': ['security', 'testing']},
    {'name': 'ビッグデータ', 'description': 'Hadoop、Spark', 'category': 'technical', 'tags': ['data', 'scalable']},
    {'name': 'コンテナ技術', 'description': 'Docker、Kubernetes', 'category': 'technical', 'tags': ['deployment', 'portable']},
    {'name': 'サーバーレス', 'description': 'Lambda、Functions', 'category': 'technical', 'tags': ['serverless', 'efficient']},
    
    # 🎯 ビジネス・キャリア (30個)
    {'name': 'マネジメント', 'description': 'チープ管理、リーダーシップ', 'category': 'business', 'tags': ['leadership', 'organizational']},
    {'name': 'プロジェクト管理', 'description': 'PM、スケジュール管理', 'category': 'business', 'tags': ['planning', 'coordinating']},
    {'name': 'コンサルティング', 'description': '問題解決、改善提案', 'category': 'business', 'tags': ['advisory', 'strategic']},
    {'name': 'セールス', 'description': '営業、販売', 'category': 'business', 'tags': ['persuasive', 'relationship']},
    {'name': 'マーケティング', 'description': 'ブランディング、プロモーション', 'category': 'business', 'tags': ['creative', 'strategic']},
    {'name': 'HR', 'description': '人事、採用', 'category': 'business', 'tags': ['people', 'organizational']},
    {'name': '財務', 'description': '会計、予算管理', 'category': 'business', 'tags': ['numerical', 'analytical']},
    {'name': 'ファイナンス', 'description': '投資、資金調達', 'category': 'business', 'tags': ['financial', 'strategic']},
    {'name': '法務', 'description': '契約、コンプライアンス', 'category': 'business', 'tags': ['legal', 'protective']},
    {'name': '起業', 'description': 'スタートアップ、新規事業', 'category': 'business', 'tags': ['entrepreneurial', 'innovative']},
    {'name': 'フランチャイズ', 'description': 'FC事業', 'category': 'business', 'tags': ['systematic', 'scalable']},
    {'name': 'eコマース', 'description': 'オンライン販売', 'category': 'business', 'tags': ['digital', 'commercial']},
    {'name': 'ロジスティクス', 'description': '物流、供給管理', 'category': 'business', 'tags': ['operational', 'efficient']},
    {'name': 'リテール', 'description': '小売業', 'category': 'business', 'tags': ['customer-facing', 'service']},
    {'name': 'B2B', 'description': '企業間取引', 'category': 'business', 'tags': ['relationship', 'professional']},
    {'name': 'B2C', 'description': '個人向けビジネス', 'category': 'business', 'tags': ['consumer', 'accessible']},
    {'name': 'SaaS', 'description': 'ソフトウェアサービス', 'category': 'business', 'tags': ['subscription', 'scalable']},
    {'name': 'アフィリエイト', 'description': '成果報酬型広告', 'category': 'business', 'tags': ['performance', 'passive']},
    {'name': 'ブランディング', 'description': 'ブランド構築', 'category': 'business', 'tags': ['identity', 'creative']},
    {'name': 'PR', 'description': '広報、パブリシティ', 'category': 'business', 'tags': ['communication', 'relationship']},
    {'name': 'IR', 'description': '投資家向け広報', 'category': 'business', 'tags': ['financial', 'communication']},
    {'name': 'M&A', 'description': '企業買収・合併', 'category': 'business', 'tags': ['strategic', 'financial']},
    {'name': 'IPO', 'description': '株式公開', 'category': 'business', 'tags': ['financial', 'growth']},
    {'name': 'ベンチャー投資', 'description': 'VC、エンジェル投資', 'category': 'business', 'tags': ['investment', 'risk']},
    {'name': 'クラウドファンディング', 'description': '資金調達', 'category': 'business', 'tags': ['crowdsourced', 'innovative']},
    {'name': 'ソーシャルビジネス', 'description': '社会課題解決', 'category': 'business', 'tags': ['social', 'impact']},
    {'name': 'サステナビリティ', 'description': '持続可能性', 'category': 'business', 'tags': ['environmental', 'responsible']},
    {'name': 'CSR', 'description': '企業社会責任', 'category': 'business', 'tags': ['social', 'responsible']},
    {'name': 'ESG投資', 'description': '環境・社会・ガバナンス', 'category': 'business', 'tags': ['sustainable', 'ethical']},
    {'name': 'リスク管理', 'description': 'リスクアセスメント', 'category': 'business', 'tags': ['analytical', 'protective']},
    
    # 🧠 自己開発・ウェルネス (35個)
    {'name': 'マインドフルネス', 'description': '瞑想、今この瞬間', 'category': 'wellness', 'tags': ['mindful', 'present']},
    {'name': 'ストレス管理', 'description': 'リラクゼーション', 'category': 'wellness', 'tags': ['stress-relief', 'balance']},
    {'name': '睡眠改善', 'description': '質の良い睡眠', 'category': 'wellness', 'tags': ['restorative', 'health']},
    {'name': '栄養学', 'description': '食事と健康', 'category': 'wellness', 'tags': ['nutritional', 'health']},
    {'name': 'デトックス', 'description': '体内浄化', 'category': 'wellness', 'tags': ['cleansing', 'health']},
    {'name': 'アロマテラピー', 'description': '香りによる癒し', 'category': 'wellness', 'tags': ['therapeutic', 'sensory']},
    {'name': 'マッサージ', 'description': '体のケア', 'category': 'wellness', 'tags': ['therapeutic', 'relaxing']},
    {'name': 'スパ', 'description': '美容・健康施設', 'category': 'wellness', 'tags': ['luxury', 'relaxing']},
    {'name': 'サウナ', 'description': '温浴・発汗', 'category': 'wellness', 'tags': ['therapeutic', 'detoxifying']},
    {'name': '温泉療法', 'description': '温泉による健康法', 'category': 'wellness', 'tags': ['therapeutic', 'traditional']},
    {'name': 'ハーブ', 'description': '薬草、自然療法', 'category': 'wellness', 'tags': ['natural', 'healing']},
    {'name': 'サプリメント', 'description': '栄養補助食品', 'category': 'wellness', 'tags': ['supplementary', 'health']},
    {'name': 'ファスティング', 'description': '断食、プチ断食', 'category': 'wellness', 'tags': ['cleansing', 'disciplined']},
    {'name': 'ピラティス', 'description': 'コア強化エクササイズ', 'category': 'wellness', 'tags': ['core', 'balanced']},
    {'name': 'ストレッチ', 'description': '柔軟性向上', 'category': 'wellness', 'tags': ['flexibility', 'maintenance']},
    {'name': '姿勢改善', 'description': '正しい姿勢づくり', 'category': 'wellness', 'tags': ['posture', 'health']},
    {'name': '呼吸法', 'description': '深呼吸、腹式呼吸', 'category': 'wellness', 'tags': ['breathing', 'calming']},
    {'name': 'セルフケア', 'description': '自分へのケア', 'category': 'wellness', 'tags': ['self-care', 'nurturing']},
    {'name': 'ライフバランス', 'description': '仕事と生活の調和', 'category': 'wellness', 'tags': ['balance', 'harmony']},
    {'name': '時間管理', 'description': '効率的な時間使用', 'category': 'wellness', 'tags': ['productivity', 'organized']},
    {'name': 'ライフハック', 'description': '生活の工夫', 'category': 'wellness', 'tags': ['efficient', 'optimized']},
    {'name': '習慣化', 'description': '良い習慣づくり', 'category': 'wellness', 'tags': ['consistent', 'improvement']},
    {'name': '目標設定', 'description': 'ゴール設定と達成', 'category': 'wellness', 'tags': ['achievement', 'focused']},
    {'name': 'モチベーション', 'description': 'やる気向上', 'category': 'wellness', 'tags': ['motivational', 'energizing']},
    {'name': 'ポジティブシンキング', 'description': '前向きな思考', 'category': 'wellness', 'tags': ['positive', 'optimistic']},
    {'name': 'グラティテュード', 'description': '感謝の気持ち', 'category': 'wellness', 'tags': ['grateful', 'appreciative']},
    {'name': 'ジャーナリング', 'description': '日記・記録', 'category': 'wellness', 'tags': ['reflective', 'introspective']},
    {'name': 'アファメーション', 'description': '肯定的な言葉', 'category': 'wellness', 'tags': ['positive', 'self-affirming']},
    {'name': 'ビジュアライゼーション', 'description': 'イメージ化', 'category': 'wellness', 'tags': ['visualization', 'goal-oriented']},
    {'name': 'コーチング', 'description': '自己実現サポート', 'category': 'wellness', 'tags': ['growth', 'supportive']},
    {'name': 'メンタリング', 'description': '指導・助言', 'category': 'wellness', 'tags': ['guidance', 'developmental']},
    {'name': 'ネットワーキング', 'description': '人脈づくり', 'category': 'wellness', 'tags': ['social', 'professional']},
    {'name': 'コミュニケーション', 'description': '対話スキル', 'category': 'wellness', 'tags': ['interpersonal', 'connective']},
    {'name': 'プレゼンテーション', 'description': '発表スキル', 'category': 'wellness', 'tags': ['presentation', 'confident']},
    {'name': 'リーダーシップ', 'description': '指導力', 'category': 'wellness', 'tags': ['leadership', 'influential']},
]

def create_interests():
    """興味関心データ作成（高速化版）"""
    start_time = time()
    print("🎯 興味関心データを作成中...")
    
    interests_data = EXPANDED_INTERESTS_DATA
    
    # バッチ処理で高速化
    with transaction.atomic():
        created_count = 0
        existing_names = set(Interest.objects.values_list('name', flat=True))
        
        new_interests = []
        for interest in interests_data:
            if interest['name'] not in existing_names:
                new_interests.append(Interest(
                    name=interest['name'],
                    category=interest['category'],
                    description=interest['description'],
                    is_official=True
                ))
                created_count += 1
        
        if new_interests:
            Interest.objects.bulk_create(new_interests)
            print(f'✅ バッチ処理で {len(new_interests)} 件作成')
    
    elapsed_time = time() - start_time
    print(f'🎯 興味関心データ作成完了！（新規作成: {created_count}個, {elapsed_time:.2f}秒）')
    return created_count

def create_users():
    """サンプルユーザーデータ作成"""
    start_time = time()
    print("👥 サンプルユーザーデータを作成中...")
    users_data = [
        # === オリジナルユーザー（10人）===
        ('田中太郎', 'tanaka', 'プログラミングが好きな大学生です'),
        ('佐藤花子', 'sato', '読書と映画鑑賞が趣味です'),
        ('山田次郎', 'yamada', 'スポーツ全般が大好きです'),
        ('鈴木美咲', 'suzuki', '料理とカフェ巡りが趣味です'),
        ('高橋健太', 'takahashi', '旅行と写真撮影が好きです'),
        ('伊藤あい', 'ito', 'ヨガと瞑想を日課にしています'),
        ('渡辺大樹', 'watanabe', 'ゲームとアニメが大好きです'),
        ('中村さくら', 'nakamura', 'ガーデニングとDIYが趣味です'),
        ('小林ゆう', 'kobayashi', '音楽と美術に興味があります'),
        ('加藤りょう', 'kato', '語学学習と投資に取り組んでいます'),
        
        # === 追加ユーザー（30人）===
        ('松本裕子', 'matsumoto', 'Webデザイナー志望の学生。UI/UXに興味があります'),
        ('森川健司', 'morikawa', 'AI・機械学習エンジニア。Pythonとデータ分析が得意'),
        ('吉田みなみ', 'yoshida', 'フルスタックエンジニア。React、Node.jsが好き'),
        ('井上翔太', 'inoue', 'iOSアプリ開発を学習中。Swiftで面白いアプリを作りたい'),
        ('岡田真理', 'okada', 'セキュリティエンジニア。サイバーセキュリティに興味'),
        ('橋本拓也', 'hashimoto', 'クラウドエンジニア。AWS、Dockerを勉強中'),
        ('木村ひかり', 'kimura', 'フロントエンドエンジニア。TypeScript、Vue.jsが得意'),
        ('清水颯', 'shimizu', 'ゲーム開発者志望。Unityでインディーゲームを制作'),
        ('内田愛美', 'uchida', 'データサイエンティスト。統計学とPythonが好き'),
        ('長谷川誠', 'hasegawa', 'DevOpsエンジニア。CI/CDとKubernetesに興味'),
        
        ('野村康平', 'nomura', 'マラソンランナー。毎日10km走っています'),
        ('坂本美優', 'sakamoto', 'ヨガインストラクター資格取得中。心と体の健康を大切に'),
        ('青木大輔', 'aoki', '筋トレ歴5年。ボディビル大会出場が目標'),
        ('西村麻衣', 'nishimura', 'ダンサー。ヒップホップとジャズダンスが得意'),
        ('藤田聡', 'fujita', 'テニスコーチ。週末は必ずコートに立っています'),
        ('石井あゆみ', 'ishii', '登山愛好家。日本百名山制覇を目指しています'),
        ('原田凛', 'harada', 'バドミントン部主将。技術向上に日々努力'),
        ('平野剛', 'hirano', 'サイクリスト。ロードバイクで日本一周が夢'),
        ('小川美穂', 'ogawa', '水泳インストラクター。4泳法すべて得意'),
        ('中島ケン', 'nakajima', 'ボルダリング愛好家。週3でジムに通っています'),
        
        ('河野美香', 'kono', '映画評論家志望。年間300本以上鑑賞'),
        ('斎藤慎一', 'saito', 'アニメ・マンガ研究家。コミケで同人誌販売'),
        ('今井ななみ', 'imai', '読書家。月20冊以上読んでブログに感想を書いています'),
        ('池田隆', 'ikeda', 'ボードゲーム愛好家。新作ゲームの情報収集が趣味'),
        ('遠藤薫', 'endo', 'フォトグラファー。ポートレート撮影が得意'),
        ('金子雅人', 'kaneko', 'ミュージシャン。バンドでギターを担当'),
        ('土屋綾', 'tsuchiya', 'ハンドメイド作家。アクセサリーやバッグを制作'),
        ('山口智也', 'yamaguchi', 'eスポーツプレイヤー。FPSゲームが得意'),
        ('関根美里', 'sekine', '書道家。師範免許を持っています'),
        ('杉山勇気', 'sugiyama', '天体観測マニア。天体写真撮影が趣味'),
        
        ('新井咲良', 'arai', 'パティシエ志望。お菓子作りが大好き'),
        ('福田雄一', 'fukuda', 'ソムリエ資格保有。ワインと料理のペアリングが得意'),
        ('大野かおり', 'ono', '料理研究家志望。各国料理を研究中'),
        ('村上浩二', 'murakami', 'ラーメン評論家。年間500杯以上食べ歩き'),
        ('横山千尋', 'yokoyama', 'カフェオーナー志望。コーヒーの知識を深めています'),
        
        ('古川真', 'furukawa', '都内散策ガイド。隠れた名所を発見するのが得意'),
        ('岩田美沙', 'iwata', '旅行プランナー。効率的な旅程作成が趣味'),
        ('菅原孝', 'sugawara', '温泉ソムリエ。全国の温泉を巡っています'),
        ('宮本理恵', 'miyamoto', '美術館学芸員志望。アート鑑賞が日課'),
        ('千葉直樹', 'chiba', 'インスタグラマー。フォトジェニックなスポット探しが得意')
    ]
    
    emotions = ['楽しい', '穏やか', 'やる気満々', 'リラックス', '集中中', '好奇心旺盛']
    
    with transaction.atomic():
        created_count = 0
        existing_usernames = set(User.objects.values_list('username', flat=True))
        
        new_users = []
        for display_name, username, bio in users_data:
            if username not in existing_usernames:
                user = User(
                    username=username,
                    display_name=display_name,
                    bio=bio,
                    emotion_state=random.choice(emotions),
                    email=f'{username}@example.com'
                )
                user.set_password('password123')
                new_users.append(user)
                created_count += 1
        
        if new_users:
            User.objects.bulk_create(new_users)
            print(f'✅ バッチ処理で {len(new_users)} 人作成')
    
    elapsed_time = time() - start_time
    print(f'👥 サンプルユーザーデータ作成完了！（新規作成: {created_count}人, {elapsed_time:.2f}秒）')
    return created_count

def create_circles():
    """サークルダミーデータ作成"""
    from knest_backend.apps.circles.models import Circle, Category
    from datetime import timezone, datetime
    
    start_time = time()
    print("🎪 サークルダミーデータを作成中...")
    
    # カテゴリデータ（slugフィールドを削除）
    categories_data = [
        ('技術・学習', 'プログラミング、IT技術、学術研究など'),
        ('スポーツ・健康', '運動、フィットネス、スポーツ競技など'),
        ('娯楽・趣味', 'ゲーム、映画、音楽、アートなど'),
        ('食べ物・料理', '料理、グルメ、レストランなど'),
        ('旅行・お出かけ', '旅行、散策、観光など'),
    ]
    
    # サークルデータ（大幅拡充版 - 50サークル）
    circles_data = [
        # === 技術・学習系（15サークル）===
        ('iOS開発サークル', 'iOSアプリ開発を学ぶサークルです。初心者から上級者まで歓迎！一緒にアプリを作りましょう。', '技術・学習', ['iOS', 'Swift', 'プログラミング', 'アプリ開発']),
        ('デザイン研究会', 'UI/UXデザインを学ぶ研究会です。デザインツールの使い方からユーザビリティまで幅広く学習。', '技術・学習', ['デザイン', 'UI/UX', 'Figma', 'クリエイティブ']),
        ('Python学習グループ', 'Pythonを基礎から学び、機械学習やデータ分析に挑戦しよう！', '技術・学習', ['Python', 'プログラミング', 'AI', 'データサイエンス']),
        ('Web開発部', 'React、Vue.js、Node.jsを使った現代的なWeb開発を学習。フルスタック開発者を目指そう！', '技術・学習', ['Web開発', 'JavaScript', 'React', 'Node.js']),
        ('ゲーム開発同好会', 'UnityやUnreal Engineを使ったゲーム開発。初心者歓迎、一緒に楽しいゲームを作ろう！', '技術・学習', ['ゲーム開発', 'Unity', '3D', 'プログラミング']),
        ('AI・機械学習研究会', '人工知能と機械学習の最新技術を研究。TensorFlowやPyTorchを使った実践的な学習。', '技術・学習', ['AI', '機械学習', 'Python', 'データサイエンス']),
        ('クラウド技術勉強会', 'AWS、Azure、GCPなどのクラウドサービスを学習。資格取得もサポート！', '技術・学習', ['AWS', 'クラウド', 'インフラ', 'DevOps']),
        ('ブロックチェーン研究室', '暗号通貨、NFT、DeFiなどブロックチェーン技術の最先端を学ぼう。', '技術・学習', ['ブロックチェーン', '暗号通貨', 'Web3', 'NFT']),
        ('データベース設計の会', 'SQL、NoSQL、設計パターンを学び、効率的なデータベースシステムを構築。', '技術・学習', ['データベース', 'SQL', '設計', 'システム']),
        ('セキュリティ勉強会', 'サイバーセキュリティの基礎から応用まで。ハッキング演習で実践的に学習。', '技術・学習', ['セキュリティ', 'ハッキング', 'ネットワーク', 'サイバー']),
        ('プロダクトマネジメント研究会', 'PM/PdMのスキルを学び、ユーザー中心の製品開発手法を身につけよう。', '技術・学習', ['プロダクト', 'マネジメント', 'UX', 'ビジネス']),
        ('フロントエンド技術部', 'モダンなフロントエンド技術を追求。React、Vue、TypeScriptで美しいUIを作ろう。', '技術・学習', ['フロントエンド', 'TypeScript', 'CSS', 'UI']),
        ('モバイルアプリ開発者の集い', 'iOS、Android、Flutter、React Nativeでクロスプラットフォーム開発を学習。', '技術・学習', ['モバイル', 'Flutter', 'React Native', 'アプリ']),
        ('DevOps実践会', 'CI/CD、Docker、Kubernetesを使った効率的な開発運用を実践。', '技術・学習', ['DevOps', 'Docker', 'Kubernetes', 'CI/CD']),
        ('エンジニア転職支援会', '未経験からエンジニア転職を目指す人のための学習・就活サポートコミュニティ。', '技術・学習', ['転職', 'キャリア', 'エンジニア', '学習']),

        # === スポーツ・健康系（12サークル）===
        ('フットサル同好会', '毎週末フットサルを楽しんでいます。初心者大歓迎！みんなでワイワイ楽しみましょう。', 'スポーツ・健康', ['フットサル', 'サッカー', 'スポーツ', '運動']),
        ('ランニングクラブ', '朝活ランニングから本格マラソン練習まで。皇居周辺を中心に活動中！', 'スポーツ・健康', ['ランニング', 'マラソン', '朝活', '健康']),
        ('ヨガ・瞑想サークル', '心と体を整えるヨガと瞑想の時間。初心者向けのゆったりクラスも開催。', 'スポーツ・健康', ['ヨガ', '瞑想', 'マインドフルネス', 'リラックス']),
        ('筋トレ・ボディメイク部', 'ジムでの筋力トレーニングと食事管理で理想の体を目指そう！', 'スポーツ・健康', ['筋トレ', 'ジム', 'ボディメイク', 'フィットネス']),
        ('バドミントンサークル', '老若男女問わず楽しめるバドミントン。技術向上と親睦を深めています。', 'スポーツ・健康', ['バドミントン', 'ラケット', 'スポーツ', '親睦']),
        ('テニス愛好会', '週末のテニスで汗を流そう！レベル別練習で着実にスキルアップ。', 'スポーツ・健康', ['テニス', 'ラケット', 'スポーツ', '練習']),
        ('登山・ハイキング部', '関東近郊の山を中心に、自然を楽しみながら体力づくり。絶景スポット巡り！', 'スポーツ・健康', ['登山', 'ハイキング', '自然', '絶景']),
        ('ダンス愛好会', 'ヒップホップからバレエまで様々なジャンルのダンスを楽しもう！', 'スポーツ・健康', ['ダンス', 'ヒップホップ', '表現', 'パフォーマンス']),
        ('水泳サークル', 'プールでの水泳練習とアクアエクササイズ。泳力向上と健康維持を目指そう。', 'スポーツ・健康', ['水泳', 'プール', '有酸素運動', '健康']),
        ('ボルダリング部', '室内クライミングで全身を使った運動。初心者向けの基礎講習も実施。', 'スポーツ・健康', ['ボルダリング', 'クライミング', '全身運動', 'チャレンジ']),
        ('サイクリング同好会', '都内・近郊をサイクリング。美しい景色を見ながら健康的にサイクリング！', 'スポーツ・健康', ['サイクリング', '自転車', '景色', '健康']),
        ('格闘技研究会', '空手、柔道、ボクシングなど様々な格闘技を体験。護身術も学べます。', 'スポーツ・健康', ['格闘技', '空手', '護身術', '武道']),

        # === 娯楽・趣味系（12サークル）===
        ('読書クラブ', '月1冊の本を読んで感想を共有します。ジャンル問わず、様々な本に出会える読書サークル。', '娯楽・趣味', ['読書', '文学', '小説', 'ビジネス書']),
        ('アニメ・マンガ研究会', '最新アニメから名作まで、アニメとマンガについて熱く語り合おう！', '娯楽・趣味', ['アニメ', 'マンガ', 'オタク', 'サブカルチャー']),
        ('映画鑑賞サークル', '話題の新作から古典の名作まで、様々な映画を一緒に楽しもう。', '娯楽・趣味', ['映画', 'シネマ', '鑑賞', 'エンターテイメント']),
        ('ボードゲーム会', '戦略ゲームからパーティーゲームまで、ボードゲームで楽しい時間を過ごそう！', '娯楽・趣味', ['ボードゲーム', 'カードゲーム', '戦略', 'パーティー']),
        ('写真愛好会', '風景、ポートレート、街角スナップなど、写真撮影の技術と楽しさを共有。', '娯楽・趣味', ['写真', 'カメラ', '撮影', 'アート']),
        ('音楽愛好会', '楽器演奏からDTMまで、音楽を愛する人たちの集まり。セッションも開催！', '娯楽・趣味', ['音楽', '楽器', 'DTM', 'セッション']),
        ('手作り・DIYサークル', '木工、手芸、アクセサリー作りなど、手作りの楽しさを分かち合おう。', '娯楽・趣味', ['DIY', '手作り', '木工', 'ハンドメイド']),
        ('ゲーム愛好会', 'PCゲーム、コンシューマーゲーム、スマホゲームを楽しむコミュニティ。', '娯楽・趣味', ['ゲーム', 'eスポーツ', 'PC', 'コンシューマー']),
        ('書道・カリグラフィー部', '美しい文字を書く技術を磨き、心を落ち着かせる時間を共有。', '娯楽・趣味', ['書道', 'カリグラフィー', '文字', '芸術']),
        ('謎解き・脱出ゲーム愛好会', '謎解きイベントや脱出ゲームを一緒に楽しむ頭脳派集団！', '娯楽・趣味', ['謎解き', '脱出ゲーム', '推理', '頭脳']),
        ('天体観測サークル', '星空を眺めて宇宙の神秘を感じよう。天体望遠鏡を使った本格観測も。', '娯楽・趣味', ['天体観測', '星空', '宇宙', '望遠鏡']),
        ('イラスト・絵画同好会', 'デジタルイラストから水彩画まで、絵を描く楽しさを共有しよう。', '娯楽・趣味', ['イラスト', '絵画', 'アート', 'デジタル']),

        # === 食べ物・料理系（6サークル）===
        ('カフェ巡りの会', '都内のおしゃれなカフェを巡ります。美味しいコーヒーとスイーツを求めて新しいお店を開拓。', '食べ物・料理', ['カフェ', 'コーヒー', 'スイーツ', 'グルメ']),
        ('料理教室サークル', '家庭料理から本格的な料理まで、みんなで作って食べて楽しもう！', '食べ物・料理', ['料理', 'レシピ', 'クッキング', '家庭料理']),
        ('ワイン愛好会', 'ワインテイスティングと料理とのペアリングを楽しむ大人のサークル。', '食べ物・料理', ['ワイン', 'テイスティング', 'ペアリング', 'お酒']),
        ('お菓子作りサークル', 'ケーキ、クッキー、和菓子まで、甘いお菓子作りを一緒に楽しもう。', '食べ物・料理', ['お菓子', 'スイーツ', 'ベーキング', '手作り']),
        ('ラーメン研究会', '都内の美味しいラーメン店を巡り、ラーメンの奥深さを探求しよう！', '食べ物・料理', ['ラーメン', 'グルメ', '食べ歩き', '探求']),
        ('国際料理愛好会', '世界各国の料理を作って味わい、文化の違いも学ぼう。', '食べ物・料理', ['国際料理', '世界', '文化', '多様性']),

        # === 旅行・お出かけ系（5サークル）===
        ('都内散策サークル', '東京の隠れた名所や話題のスポットを一緒に巡ろう！新しい発見がきっとある。', '旅行・お出かけ', ['散策', '東京', '観光', '発見']),
        ('週末プチ旅行の会', '関東近郊の日帰り旅行や一泊旅行で、リフレッシュしませんか？', '旅行・お出かけ', ['旅行', '日帰り', '関東', 'リフレッシュ']),
        ('温泉巡りサークル', '癒しの温泉を求めて全国の名湯を訪問。心も体もリラックス。', '旅行・お出かけ', ['温泉', '癒し', 'リラックス', '名湯']),
        ('美術館・博物館めぐり', 'アートや歴史に触れる知的な時間。様々な展示を一緒に楽しもう。', '旅行・お出かけ', ['美術館', '博物館', 'アート', '文化']),
        ('フォトウォーク部', '街歩きしながら写真撮影。インスタ映えスポットから隠れた名所まで。', '旅行・お出かけ', ['フォトウォーク', '写真', '街歩き', 'インスタ'])
    ]
    
    with transaction.atomic():
        created_categories = 0
        created_circles = 0
        
        # 管理ユーザーまたは最初のユーザーを取得
        try:
            admin_user = User.objects.filter(is_superuser=True).first()
            if not admin_user:
                admin_user = User.objects.first()
                if not admin_user:
                    print("❌ ユーザーが存在しません。先にユーザーを作成してください。")
                    return 0
        except Exception as e:
            print(f"❌ ユーザー取得エラー: {e}")
            return 0
        
        # カテゴリ作成（slugフィールドを削除）
        existing_categories = set(Category.objects.values_list('name', flat=True))
        for name, description in categories_data:
            if name not in existing_categories:
                Category.objects.create(
                    name=name,
                    description=description
                )
                created_categories += 1
                print(f"  ✅ カテゴリ '{name}' 作成")
        
        # サークル作成
        existing_circles = set(Circle.objects.values_list('name', flat=True))
        print(f"  既存サークル: {len(existing_circles)}個")
        
        for name, description, category_name, tags in circles_data:
            if name not in existing_circles:
                try:
                    category = Category.objects.get(name=category_name)
                    circle = Circle.objects.create(
                        name=name,
                        description=description,
                        status='open',
                        circle_type='public',
                        creator=admin_user,
                        owner=admin_user,
                        member_count=random.randint(5, 25),
                        post_count=random.randint(10, 50),
                        tags=tags,
                        last_activity=datetime.now(timezone.utc)
                    )
                    # ManyToManyフィールドはcreate後に追加
                    circle.categories.add(category)
                    created_circles += 1
                    print(f"  ✅ サークル '{name}' 作成 (ID: {circle.id})")
                except Category.DoesNotExist:
                    print(f"  ❌ カテゴリ '{category_name}' が見つかりません")
                except Exception as e:
                    print(f"  ❌ サークル '{name}' 作成エラー: {e}")
            else:
                print(f"  📌 サークル '{name}' は既に存在します")
    
    elapsed_time = time() - start_time
    print(f'🎪 サークルダミーデータ作成完了！（カテゴリ: {created_categories}個, サークル: {created_circles}個, {elapsed_time:.2f}秒）')
    return created_circles

def main():
    """メイン処理"""
    if len(sys.argv) < 2:
        print("使用方法: python create_sample_data.py [interests|users|circles|all]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'interests':
        create_interests()
    elif command == 'users':
        create_users()
    elif command == 'circles':
        create_circles()
    elif command == 'all':
        print("🎉 基本初期データ作成を開始します...")
        interests_count = create_interests()
        users_count = create_users()
        circles_count = create_circles()
        print("\n🎉 基本初期データ作成完了！")
        print(f"📊 作成されたデータ:")
        print(f"  - 興味関心: {interests_count}個")
        print(f"  - ユーザー: {users_count}人")
        print(f"  - サークル: {circles_count}個")
    else:
        print(f"❌ 不明なコマンド: {command}")
        print("使用可能なコマンド: interests, users, circles, all")
        sys.exit(1)

if __name__ == '__main__':
    main() 