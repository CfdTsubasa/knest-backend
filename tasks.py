"""
開発タスク管理用スクリプト
使用方法: pip install invoke && invoke --list
"""
from invoke import task
import os


@task
def setup(c):
    """初回セットアップ（仮想環境作成 + 依存関係インストール）"""
    print("📦 仮想環境を作成しています...")
    c.run("python -m venv venv")
    
    print("🔧 依存パッケージをインストールしています...")
    c.run("./venv/bin/pip install -r requirements.txt")
    
    print("🗃️ データベースマイグレーションを実行しています...")
    c.run("./venv/bin/python manage.py migrate")
    
    print("✅ セットアップ完了！'invoke dev' で開発サーバーを起動できます")


@task
def dev(c):
    """開発サーバー起動"""
    print("🚀 開発サーバーを起動しています...")
    print("🌐 http://localhost:8000 でアクセスできます")
    print("📚 API文書: http://localhost:8000/swagger/")
    c.run("./venv/bin/python manage.py runserver")


@task
def migrate(c):
    """データベースマイグレーション"""
    c.run("./venv/bin/python manage.py migrate")


@task
def test(c):
    """テスト実行"""
    c.run("./venv/bin/python manage.py test")


@task
def clean(c):
    """仮想環境とキャッシュファイルを削除"""
    c.run("rm -rf venv/")
    c.run("find . -type d -name '__pycache__' -delete")
    c.run("find . -type f -name '*.pyc' -delete") 