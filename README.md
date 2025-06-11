# Knest Backend API

## 📖 概要
Knestは趣味・興味関心に基づいたサークル発見・参加プラットフォームのバックエンドAPIです。

## 🚀 技術スタック
- **Backend**: Django 4.2.22 + Django REST Framework
- **Database**: SQLite (開発環境) / PostgreSQL (本番環境)
- **Cache**: Django DummyCache (開発環境) / Redis (本番環境)
- **Authentication**: JWT Token認証
- **API Documentation**: drf-yasg (Swagger)

## 🎯 主要機能
- **ユーザー認証・管理**: JWT認証、ユーザープロフィール
- **サークル管理**: 作成、参加、退会、検索、推薦
- **チャット機能**: リアルタイムチャット、メッセージ履歴
- **興味関心システム**: 3階層（カテゴリ→サブカテゴリ→タグ）
- **マッチングエンジン**: 興味・年齢・居住地による重み付けマッチング

## 🛠️ セットアップ

### 前提条件
- Python 3.9+
- pip

### インストール
```bash
# リポジトリクローン
git clone https://github.com/your-username/knest-backend.git
cd knest-backend

# 仮想環境作成・有効化
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows

# 依存関係インストール
pip install -r requirements.txt

# データベースマイグレーション
python manage.py makemigrations
python manage.py migrate

# スーパーユーザー作成
python manage.py createsuperuser

# サンプルデータ作成（オプション）
python simple_testuser_setup.py
python create_hierarchical_sample_data.py
```

### 起動
```bash
# 開発サーバー起動
python manage.py runserver 8000

# または Makeコマンド使用
make dev
```

## 📚 API エンドポイント

### 認証
- `POST /api/users/auth/token/` - ログイン
- `POST /api/users/auth/token/refresh/` - トークン更新
- `GET /api/users/me/` - ユーザー情報取得

### サークル
- `GET /api/circles/` - サークル一覧
- `POST /api/circles/` - サークル作成
- `GET /api/circles/{id}/` - サークル詳細
- `GET /api/circles/circles/my/` - 参加中サークル一覧
- `POST /api/circles/{id}/join/` - サークル参加

### チャット
- `GET /api/circles/chats/?circle={id}` - チャットメッセージ取得
- `POST /api/circles/chats/` - メッセージ送信

### 興味関心
- `GET /api/interests/hierarchical/categories/` - カテゴリ一覧
- `GET /api/interests/hierarchical/subcategories/` - サブカテゴリ一覧
- `GET /api/interests/hierarchical/tags/` - タグ一覧

## 🔧 開発ツール

### Makeコマンド
```bash
make dev          # 開発サーバー起動
make test         # テスト実行
make lint         # コード品質チェック
make migrate      # マイグレーション実行
make shell        # Djangoシェル起動
```

### API文書
- **Swagger UI**: http://localhost:8000/swagger/
- **管理画面**: http://localhost:8000/admin/

## 🌐 関連リポジトリ
- **iOS アプリ**: [knest-ios-app](https://github.com/your-username/knest-ios-app)
- **ドキュメント**: [knest-docs](https://github.com/your-username/knest-docs)

## 📝 開発ガイド
詳細な開発ガイドは `docs/development_session_2025-01-27.md` を参照してください。

## 🤝 コントリビューション
プルリクエストやIssueの作成を歓迎します。

## 📄 ライセンス
このプロジェクトはMITライセンスの下で公開されています。 