# Knest Backend

Knestは、興味や感情を共有し、AIによるサポートを受けられるソーシャルプラットフォームのバックエンドAPIです。

## 機能概要

- ユーザー管理と認証
- 興味・関心の管理
- AIサポートセッション
- サブスクリプション管理
- メッセージングとリアクション

詳細な機能については以下のドキュメントを参照してください：
- [アプリケーション概要](docs/app_overview.md)
- [APIエンドポイント一覧](docs/api_endpoints.md)

## 技術スタック

- Python 3.9.6
- Django 4.2.22
- Django REST Framework 3.14.0
- PostgreSQL（開発環境ではSQLite3）
- Redis
- Celery

## 🚀 クイックスタート

**最も簡単な開発環境の起動方法:**

```bash
# 初回のみ
make setup

# 開発サーバー起動
make dev
```

詳細な開発環境セットアップ方法は **[開発環境セットアップガイド](docs/development_setup.md)** を参照してください。

## 従来の開発環境セットアップ

<details>
<summary>従来の手動セットアップ方法（クリックして展開）</summary>

1. リポジトリのクローン
```bash
git clone https://github.com/your-username/knest-backend.git
cd knest-backend
```

2. 仮想環境の作成と有効化
```bash
python -m venv venv
source venv/bin/activate  # Unix系
venv\Scripts\activate     # Windows
```

3. 依存パッケージのインストール
```bash
pip install -r requirements.txt
```

4. 環境変数の設定
```bash
cp .env.example .env
# .envファイルを編集して必要な環境変数を設定
```

5. データベースのセットアップ
```bash
python manage.py migrate
```

6. 開発サーバーの起動
```bash
python manage.py runserver
```

</details>

## テスト

```bash
# 全てのテストを実行
make test
# または
python manage.py test

# 特定のアプリケーションのテストを実行
python manage.py test apps.interests
```

## API ドキュメント

開発サーバー起動後、以下のURLでSwagger UIによるAPIドキュメントにアクセスできます：

- Swagger UI: http://localhost:8000/swagger/
- ReDoc: http://localhost:8000/redoc/

## コントリビューション

1. このリポジトリをフォーク
2. 新しいブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add some amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。 