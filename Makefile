.PHONY: help install migrate runserver test clean setup dev createsuperuser backend-help ios-help status shell reset-db backup makemigrations create-sample-data create-interests create-categories create-users create-circles

# 仮想環境設定
VENV := venv
PYTHON := ./$(VENV)/bin/python
PIP := ./$(VENV)/bin/pip
MANAGE := $(PYTHON) manage.py

# 高速化設定
MAKEFLAGS += --jobs=4 --load-average=8.0

# デフォルトターゲット
help:
	@echo "🚀 Knest開発環境コマンド一覧"
	@echo "  make setup           - 初回セットアップ（仮想環境作成 + 依存関係インストール）"
	@echo "  make dev             - 開発サーバー起動"
	@echo "  make createsuperuser - 管理者ユーザー作成"
	@echo "  make install         - 依存パッケージインストール"
	@echo "  make migrate         - データベースマイグレーション"
	@echo "  make makemigrations  - マイグレーションファイル作成"
	@echo "  make test            - テスト実行"
	@echo "  make clean           - 仮想環境とキャッシュファイルを削除"
	@echo ""
	@echo "🖥️ Backend詳細操作:"
	@echo "  make shell           - Django shell起動"
	@echo "  make reset-db        - データベースリセット（警告あり）"
	@echo "  make backup          - データベースバックアップ作成"
	@echo ""
	@echo "🎭 初期データ作成 (⚡高速版):"
	@echo "  make create-sample-data - 全初期データ作成（興味関心+カテゴリ+ユーザー+サークル）"
	@echo "  make create-sample-data-fast - 🚀全初期データ高速作成（並列処理）"
	@echo "  make create-interests   - 興味関心データのみ作成"
	@echo "  make create-categories  - カテゴリデータのみ作成"
	@echo "  make create-users      - サンプルユーザーデータのみ作成"
	@echo "  make create-circles    - サンプルサークルデータのみ作成"
	@echo ""
	@echo "🔧 追加機能:"
	@echo "  make ios-help        - iOS用詳細コマンド一覧"
	@echo "  make status          - プロジェクト状態確認"

# 仮想環境チェック
check-venv:
	@if [ ! -d "$(VENV)" ]; then \
		echo "❌ 仮想環境が見つかりません"; \
		echo "💡 'make setup' を実行してください"; \
		exit 1; \
	fi

# 初回セットアップ
setup:
	@echo "📦 仮想環境を作成しています..."
	python -m venv venv
	@echo "🔧 仮想環境を有効化して依存パッケージをインストールしています..."
	./venv/bin/pip install -r requirements.txt
	@echo "🗃️ データベースマイグレーションを実行しています..."
	./venv/bin/python manage.py migrate
	@echo "✅ セットアップ完了！'make createsuperuser' で管理者ユーザーを作成してください"

# 開発サーバー起動
dev: check-venv
	@echo "🚀 開発サーバーを起動しています..."
	@echo "🌐 http://localhost:8000 でアクセスできます"
	@echo "🔧 管理画面: http://localhost:8000/admin/"
	@echo "📚 API文書: http://localhost:8000/swagger/"
	$(MANAGE) runserver

# 管理者ユーザー作成
createsuperuser: check-venv
	@echo "👤 管理者ユーザーを作成しています..."
	$(MANAGE) createsuperuser

# 依存パッケージインストール
install: check-venv
	$(PIP) install -r requirements.txt

# データベースマイグレーション
migrate: check-venv
	@echo "🗃️ Applying migrations..."
	$(MANAGE) migrate

# マイグレーションファイル作成
makemigrations: check-venv
	@echo "📝 Creating migrations..."
	$(MANAGE) makemigrations

# Django shell
shell: check-venv
	@echo "🐍 Starting Django shell..."
	$(MANAGE) shell

# データベースリセット
reset-db: check-venv
	@echo "⚠️  WARNING: This will delete all data!"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ]
	rm -f db.sqlite3
	$(MANAGE) migrate
	@echo "🗃️ Database reset complete!"

# データベースバックアップ
backup: check-venv
	@echo "💾 Creating database backup..."
	@if [ -f db.sqlite3 ]; then \
		cp db.sqlite3 "db_backup_$(shell date +%Y%m%d_%H%M%S).sqlite3"; \
		echo "✅ Backup created!"; \
	else \
		echo "❌ No database file found"; \
	fi

# テスト実行
test: check-venv
	$(MANAGE) test

# 全初期データ作成
create-sample-data: check-venv
	@echo "🎉 全初期データ作成を開始します..."
	$(PYTHON) create_sample_data.py all

# 興味関心データ作成
create-interests: check-venv
	@echo "🎯 興味関心データを作成中..."
	$(PYTHON) create_sample_data.py interests

# カテゴリデータ作成
create-categories: check-venv
	@echo "📁 カテゴリデータを作成中..."
	$(PYTHON) create_sample_data.py categories

# サンプルユーザーデータ作成
create-users: check-venv
	@echo "👥 サンプルユーザーデータを作成中..."
	$(PYTHON) create_sample_data.py users

# サンプルサークルデータ作成
create-circles: check-venv
	@echo "🎪 サンプルサークルデータを作成中..."
	$(PYTHON) create_sample_data.py circles

# クリーンアップ
clean:
	rm -rf venv/
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.pyc" -delete 

# Backend用詳細コマンド一覧（統合済み）
backend-help:
	@echo "🖥️ Backend詳細コマンド（統合済み）:"
	@echo "  make shell           - Django shell起動"
	@echo "  make migrate         - マイグレーション実行"
	@echo "  make makemigrations  - マイグレーション作成"
	@echo "  make reset-db        - DB完全リセット（警告あり）"
	@echo "  make backup          - DBバックアップ作成"
	@echo "  make test            - テスト実行"

# iOS用詳細コマンド一覧
ios-help:
	@echo "📱 iOS詳細コマンド:"
	@if [ -d "KnestApp" ]; then \
		cd KnestApp && make help; \
	else \
		echo "❌ KnestApp ディレクトリが見つかりません"; \
	fi

# プロジェクト状態確認
status:
	@echo "📊 KnestApp プロジェクト状態"
	@echo "=========================="
	@echo ""
	@echo "🗂️  プロジェクト構造:"
	@ls -la | head -10
	@echo ""
	@echo "🖥️  Backend状態:"
	@if [ -f "db.sqlite3" ]; then \
		echo "  ✅ Database: 存在"; \
	else \
		echo "  ❌ Database: 未作成 (make setup を実行してください)"; \
	fi
	@if [ -d "venv" ]; then \
		echo "  ✅ Virtual Env: 存在"; \
	else \
		echo "  ❌ Virtual Env: 未作成 (make setup を実行してください)"; \
	fi
	@if pgrep -f "python.*manage.py.*runserver" > /dev/null; then \
		echo "  ✅ Server: 稼働中"; \
	else \
		echo "  ❌ Server: 停止中"; \
	fi
	@echo ""
	@echo "📱 iOS状態:"
	@if [ -d "KnestApp/KnestApp.xcodeproj" ]; then \
		echo "  ✅ Project: 存在"; \
	else \
		echo "  ❌ Project: 未作成"; \
	fi
	@if pgrep -f "Simulator" > /dev/null; then \
		echo "  ✅ Simulator: 稼働中"; \
	else \
		echo "  ❌ Simulator: 停止中"; \
	fi

# 高速セットアップ（並列処理）
setup-fast:
	@echo "🚀 高速セットアップを開始します..."
	@echo "📦 仮想環境を作成しています..."
	python -m venv venv
	@echo "🔧 仮想環境を有効化して依存パッケージをインストールしています..."
	./venv/bin/pip install -r requirements.txt --quiet --disable-pip-version-check
	@echo "🗃️ データベースマイグレーションを実行しています..."
	./venv/bin/python manage.py migrate --verbosity=1
	@echo "✅ セットアップ完了！'make createsuperuser' で管理者ユーザーを作成してください"

# 高速初期データ作成（並列処理）
create-sample-data-fast: check-venv
	@echo "🚀 高速初期データ作成を開始します..."
	@echo "⚡ 並列処理で実行中..."
	@( \
		$(PYTHON) create_sample_data.py interests & \
		$(PYTHON) create_sample_data.py categories & \
		wait; \
		$(PYTHON) create_sample_data.py users & \
		wait; \
		$(PYTHON) create_sample_data.py circles & \
		wait \
	)
	@echo "✅ 高速初期データ作成完了！"

# データベースマイグレーション（高速版）
migrate: check-venv
	@echo "🗃️ Applying migrations..."
	$(MANAGE) migrate --verbosity=1

# 高速テスト実行
test-fast: check-venv
	$(MANAGE) test --parallel --keepdb

# 高速クリーンアップ
clean-fast:
	@echo "🧹 高速クリーンアップ中..."
	rm -rf venv/ &
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null &
	find . -type f -name "*.pyc" -delete &
	wait
	@echo "✅ クリーンアップ完了！" 