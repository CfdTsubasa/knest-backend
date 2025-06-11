#!/bin/bash

echo "🚀 Knest開発環境を起動しています..."

# 仮想環境の有効化
if [ ! -d "venv" ]; then
    echo "📦 仮想環境を作成しています..."
    python -m venv venv
fi

echo "🔧 仮想環境を有効化しています..."
source venv/bin/activate

# 依存パッケージのインストール
echo "📋 依存パッケージをインストールしています..."
pip install -r requirements.txt

# データベースマイグレーション
echo "🗃️ データベースマイグレーションを実行しています..."
python manage.py migrate

# 開発サーバーの起動
echo "✅ 開発サーバーを起動しています..."
echo "🌐 http://localhost:8000 でアクセスできます"
echo "📚 API文書: http://localhost:8000/swagger/"
python manage.py runserver 