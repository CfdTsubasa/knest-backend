# 🚀 KnestApp Makefile Guide

KnestAppプロジェクトの開発を効率化するためのMakefileコマンド集です。

## 📋 概要

このプロジェクトには3つのMakefileが含まれています：

- **Root Makefile** (`/Makefile`) - メイン開発環境（仮想環境ベース）
- **Backend Makefile** (`/knest_backend/Makefile`) - Django バックエンド詳細管理
- **iOS Makefile** (`/KnestApp/Makefile`) - iOS アプリ管理

## 🚀 クイックスタート

### 新規開発者の場合

```bash
# プロジェクトディレクトリに移動
cd knest-app

# 初回セットアップ（仮想環境作成 + 依存関係インストール）
make setup

# 管理者ユーザー作成
make createsuperuser

# 開発サーバー起動
make dev
```

### 既存開発者の場合

```bash
# 開発サーバー起動
make dev

# プロジェクト状態確認
make status
```

## 🌟 メインコマンド（Root Makefile）

### 基本操作

```bash
# ヘルプ表示
make help

# 初回セットアップ（仮想環境作成 + 依存関係インストール）
make setup

# 開発サーバー起動
make dev

# 管理者ユーザー作成
make createsuperuser

# テスト実行
make test

# プロジェクト状態確認
make status
```

### メンテナンス

```bash
# 依存パッケージインストール
make install

# データベースマイグレーション
make migrate

# クリーンアップ（仮想環境とキャッシュファイルを削除）
make clean
```

### 詳細コマンド

```bash
# Backend用詳細コマンド一覧
make backend-help

# iOS用詳細コマンド一覧  
make ios-help
```

## 🖥️ Backend 詳細コマンド

**前提条件**: ルートで `make setup` を実行済み

```bash
cd knest_backend

# ヘルプ表示
make help

# マイグレーション
make migrate
make makemigrations

# データベースリセット
make reset-db

# Django shell
make shell

# サーバー起動（Backendディレクトリから）
make server

# テスト実行
make test

# コード品質チェック（flake8が必要）
make lint

# コードフォーマット（blackが必要）
make format

# バックアップ作成
make backup

# テストデータ作成
make create-test-data
```

## 📱 iOS コマンド

```bash
cd KnestApp

# ヘルプ表示
make help

# プロジェクトビルド
make build

# シミュレーターで実行
make run

# テスト実行
make test

# シミュレーター起動
make simulator

# 利用可能なデバイス一覧
make devices

# Xcodeで開く
make open

# クリーンアップ
make clean
```

## 🔧 典型的な開発フロー

### 1. 朝の開発開始

```bash
# プロジェクトディレクトリに移動
cd knest-app

# 状態確認
make status

# 開発サーバー起動
make dev
```

### 2. 開発中

```bash
# バックエンドの詳細操作が必要な場合
cd knest_backend
make help
# 例：make shell, make reset-db など

# iOSアプリのビルド
cd ../KnestApp
make build

# メインディレクトリでテスト
cd ..
make test
```

### 3. 終了時

```bash
# サーバーは Ctrl+C で停止

# 必要に応じてバックアップ
cd knest_backend
make backup
```

## 🔍 トラブルシューティング

### よくある問題と解決法

#### 1. 仮想環境の問題

```bash
# 仮想環境を削除して再作成
make clean
make setup
```

#### 2. データベースの問題

```bash
# データベースリセット
cd knest_backend
make reset-db
```

#### 3. 依存関係の問題

```bash
# 依存関係再インストール
make install
```

#### 4. 状態がわからない

```bash
# プロジェクト状態確認
make status
```

## 🎯 使用場面別ガイド

### 新機能開発時

```bash
# 1. 最新状態に更新
make install

# 2. テストデータ作成
cd knest_backend
make create-test-data

# 3. 開発開始
cd ..
make dev
```

### データベース関連作業

```bash
cd knest_backend

# マイグレーション作成
make makemigrations

# マイグレーション適用
make migrate

# Django shell でデータ確認
make shell

# バックアップ作成
make backup
```

### デバッグ時

```bash
# Backend詳細ログ確認
cd knest_backend
make logs

# Django shell でデバッグ
make shell

# iOS デバイスログ確認
cd ../KnestApp
make logs
```

## 📚 参考情報

### 接続情報

- **Backend Server**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin/
- **API Documentation**: http://localhost:8000/swagger/

### ディレクトリ構造

```
knest-app/
├── Makefile                    # Root Makefile（メイン）
├── venv/                      # 仮想環境
├── db.sqlite3                 # データベース
├── requirements.txt           # 依存関係
├── manage.py                  # Django管理スクリプト
├── knest_backend/
│   ├── Makefile              # Backend詳細Makefile
│   └── ...
└── KnestApp/
    ├── Makefile              # iOS Makefile
    ├── KnestApp.xcodeproj
    └── ...
```

### 環境要件

- Python 3.8+
- Django 4.2+
- Xcode 15+（iOS開発時）
- iOS 17.0+（iOS開発時）

## 🎉 まとめ

### メイン開発の流れ

1. **`make setup`** - 初回セットアップ
2. **`make dev`** - 日常の開発サーバー起動
3. **`make status`** - 状態確認
4. **`make backend-help`** / **`make ios-help`** - 詳細操作

### 利点

- ✅ **既存の仕組みを維持** - venvベースの環境はそのまま
- ✅ **段階的な機能拡張** - 必要に応じて詳細操作可能
- ✅ **シンプルな日常操作** - `make dev` で開発開始
- ✅ **状態確認機能** - `make status` で一目瞭然

何か問題があれば `make help` でコマンド一覧を確認してください！ 