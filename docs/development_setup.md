# 開発環境セットアップガイド

Knest Backendの開発環境をセットアップして起動する方法をまとめています。

## 🚀 クイックスタート

### 1. 最初のセットアップ（初回のみ）

プロジェクトディレクトリに移動後、以下のいずれかの方法でセットアップを行います：

#### A. Makefile（推奨）
```bash
make setup
```

#### B. シェルスクリプト
```bash
./start_dev.sh
```

#### C. Invoke（Python製タスクランナー）
```bash
./venv/bin/invoke setup
```

### 2. 管理者ユーザーの作成（初回のみ）

Django管理画面にアクセスするためのsuperuserを作成します：

```bash
# Makefile
make createsuperuser

# または手動で
./venv/bin/python manage.py createsuperuser
```

### 3. 開発サーバーの起動

セットアップ完了後は以下のコマンドで起動できます：

#### A. Makefile（推奨）
```bash
make dev
```

#### B. Invoke
```bash
./venv/bin/invoke dev
```

#### C. 従来の方法
```bash
source venv/bin/activate
python manage.py runserver
```

### 4. アクセス

サーバー起動後、以下のURLにアクセスできます：

- **アプリケーション**: http://localhost:8000
- **Django管理画面**: http://localhost:8000/admin/
- **API文書（Swagger）**: http://localhost:8000/swagger/
- **API文書（ReDoc）**: http://localhost:8000/redoc/

## 📋 利用可能なタスク

### Makefile

```bash
make            # ヘルプ表示
make setup      # 初回セットアップ
make dev        # 開発サーバー起動
make install    # 依存パッケージインストール
make migrate    # データベースマイグレーション
make test       # テスト実行
make clean      # 仮想環境とキャッシュファイルを削除
```

### Invoke

```bash
./venv/bin/invoke --list    # タスク一覧表示
./venv/bin/invoke setup     # 初回セットアップ
./venv/bin/invoke dev       # 開発サーバー起動
./venv/bin/invoke migrate   # データベースマイグレーション
./venv/bin/invoke test      # テスト実行
./venv/bin/invoke clean     # クリーンアップ
```

### エイリアス設定（任意）

Invokeを頻繁に使う場合は、`~/.zshrc`にエイリアスを追加できます：

```bash
echo 'alias inv="./venv/bin/invoke"' >> ~/.zshrc
source ~/.zshrc

# 使用例
inv dev
inv migrate
inv test
```

## 🔧 手動セットアップ（詳細）

自動化ツールを使わずに手動でセットアップしたい場合：

### 1. 仮想環境の作成
```bash
python -m venv venv
```

### 2. 仮想環境の有効化
```bash
source venv/bin/activate  # macOS/Linux
# または
venv\Scripts\activate     # Windows
```

### 3. 依存パッケージのインストール
```bash
pip install -r requirements.txt
```

### 4. データベースマイグレーション
```bash
python manage.py migrate
```

### 5. 開発サーバーの起動
```bash
python manage.py runserver
```

## 🧪 テストの実行

```bash
# 全てのテストを実行
make test
# または
./venv/bin/invoke test
# または
python manage.py test

# 特定のアプリケーションのテストを実行
python manage.py test apps.interests
```

## 🧹 環境のクリーンアップ

開発環境をリセットしたい場合：

```bash
make clean
# または
./venv/bin/invoke clean
```

これにより以下が削除されます：
- 仮想環境（`venv/`ディレクトリ）
- Pythonキャッシュファイル（`__pycache__`、`*.pyc`）

## ❓ トラブルシューティング

### よくある問題

1. **`make`コマンドが見つからない**
   - macOS: `xcode-select --install`
   - Ubuntu/Debian: `sudo apt install build-essential`

2. **仮想環境のPythonバージョンが古い**
   ```bash
   make clean
   python3.9 -m venv venv  # 明示的にPython 3.9を指定
   make setup
   ```

3. **依存関係のインストールエラー**
   ```bash
   ./venv/bin/pip install --upgrade pip
   make install
   ```

4. **データベースエラー**
   ```bash
   rm db.sqlite3  # SQLiteファイルを削除
   make migrate   # マイグレーションを再実行
   ```

## 📚 関連ドキュメント

- [アプリケーション概要](app_overview.md)
- [APIエンドポイント一覧](api_endpoints.md)
- [API詳細文書](api_documentation.md) 