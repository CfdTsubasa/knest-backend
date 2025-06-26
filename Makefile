.PHONY: help install migrate runserver test clean setup dev createsuperuser backend-help ios-help status shell reset-db backup makemigrations create-sample-data create-interests create-categories create-users create-circles

# 仮想環境設定
VENV := venv
PYTHON := ./$(VENV)/bin/python3
PIP := ./$(VENV)/bin/pip
MANAGE := $(PYTHON) manage.py

# 高速化設定
MAKEFLAGS += --jobs=4 --load-average=8.0

# デフォルトターゲット
help:
	@echo "[ROCKET] Knest開発環境コマンド一覧"
	@echo "  make setup               - 初回セットアップ (仮想環境作成+依存関係+DB+マイグレーション)"
	@echo "  make dev                 - 開発サーバー起動"
	@echo "  make createsuperuser     - 管理者ユーザー作成"
	@echo "  make install             - 依存関係再インストール"
	@echo "  make migrate             - マイグレーション実行"
	@echo "  make makemigrations      - マイグレーション作成"
	@echo "  make test                - テスト実行"
	@echo "  make clean               - 仮想環境削除 (注意)"
	@echo ""
	@echo "🖥️ Backend詳細操作:"
	@echo "  make shell               - Django shell起動"
	@echo "  make reset-db            - データベースリセット (注意)"
	@echo "  make backup              - データベースバックアップ"
	@echo ""
	@echo "🎭 初期データ作成 ([PERFORMANCE]高速版):"
	@echo "  make create-sample-data      - [PERFORMANCE]全初期データ作成（推奨）"
	@echo "  make create-sample-data-fast - [ROCKET]全初期データ高速作成（並列処理）"
	@echo "  make create-interests        - 興味関心データ"
	@echo "  make create-categories       - カテゴリデータ"
	@echo "  make create-users            - サンプルユーザー"
	@echo "  make create-circles          - サンプルサークル"
	@echo ""
	@echo "🔧 追加機能:"
	@echo "  make ios-help              - iOS用詳細コマンド一覧"
	@echo "  make status                - 現在の状態確認"

# 仮想環境チェック
check-venv:
	@if [ ! -d "$(VENV)" ]; then \
		echo "[BULB] 'make setup' を実行してください"; \
		exit 1; \
	fi

# 初回セットアップ
setup:
	@echo "[TOOLS] 仮想環境を有効化して依存パッケージをインストールしています..."
	@if [ ! -d "$(VENV)" ]; then \
		$(PYTHON) -m venv $(VENV); \
	fi
	@. $(VENV)/bin/activate && \
	pip install --upgrade pip && \
	pip install -r requirements.txt && \
	$(MANAGE) migrate && \
	echo "[COMPLETE] セットアップ完了！"
	@echo "次のステップ:"
	@echo "  make createsuperuser  # 管理者アカウント作成"
	@echo "  make create-sample-data-fast  # サンプルデータ作成"
	@echo "  make dev  # サーバー起動"

# 開発サーバー起動
dev: check-venv
	@echo "[ROCKET] 開発サーバーを起動しています..."
	@. $(VENV)/bin/activate && $(MANAGE) runserver

# 管理者ユーザー作成（個別実行用）
createsuperuser: check-venv
	@. $(VENV)/bin/activate && \
	if $(PYTHON) -c "import django; django.setup(); from django.contrib.auth.models import User; exit(0 if User.objects.filter(is_superuser=True).exists() else 1)" 2>/dev/null; then \
		echo "  [COMPLETE] 管理者ユーザー（admin）を作成しました"; \
	else \
		echo "  [COMPLETE] 管理者ユーザー（admin）が存在します"; \
	fi
	@echo "[TOOLS] 管理画面: http://localhost:8000/admin/ (admin / admin123)"

# 依存パッケージインストール
install: check-venv
	@. $(VENV)/bin/activate && $(PIP) install -r requirements.txt

# データベースマイグレーション
migrate: check-venv
	@echo "🗃️ Applying migrations..."
	@. $(VENV)/bin/activate && $(MANAGE) migrate

# マイグレーションファイル作成
makemigrations: check-venv
	@echo "📝 Creating migrations..."
	@. $(VENV)/bin/activate && $(MANAGE) makemigrations

# Django shell
shell: check-venv
	@echo "🐍 Starting Django shell..."
	@. $(VENV)/bin/activate && $(MANAGE) shell

# データベースリセット
reset-db: check-venv
	@echo "⚠️  WARNING: This will delete all data!"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ]
	rm -f db.sqlite3
	@. $(VENV)/bin/activate && $(MANAGE) migrate
	@echo "🗃️ Database reset complete!"

# データベースバックアップ
backup: check-venv
	@echo "💾 Creating database backup..."
	@if [ -f db.sqlite3 ]; then \
		timestamp=$$(date +%Y%m%d_%H%M%S); \
		cp db.sqlite3 "backup_db_$$timestamp.sqlite3"; \
		echo "✅ Backup created!"; \
	else \
		echo "❌ No database file found"; \
	fi

# テスト実行
test: check-venv
	@. $(VENV)/bin/activate && $(MANAGE) test

# 全初期データ作成
create-sample-data: check-venv
	@echo "[PARTY] 全初期データ作成を開始します..."
	@. $(VENV)/bin/activate && $(MANAGE) createsuperuser --noinput --username admin --email admin@example.com --password admin123 2>/dev/null || true
	@echo ""
	@echo "[TARGET] 興味関心データを作成中..."
	@. $(VENV)/bin/activate && $(PYTHON) create_sample_data.py
	@echo ""

# 興味関心データ作成
create-interests: check-venv
	@echo "🎯 興味関心データを作成中..."
	@. $(VENV)/bin/activate && $(PYTHON) create_sample_data.py interests

# カテゴリデータ作成
create-categories: check-venv
	@echo "📁 カテゴリデータを作成中..."
	@. $(VENV)/bin/activate && $(PYTHON) create_sample_data.py categories

# サンプルユーザーデータ作成
create-users: check-venv
	@echo "👥 サンプルユーザーデータを作成中..."
	@. $(VENV)/bin/activate && $(PYTHON) create_sample_data.py users

# サンプルサークルデータ作成
create-circles: check-venv
	@echo "🎪 サンプルサークルデータを作成中..."
	@. $(VENV)/bin/activate && $(PYTHON) create_sample_data.py circles

# クリーンアップ
clean:
	rm -rf venv/
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.pyc" -delete 

# Backend用詳細コマンド一覧（統合済み）
backend-help:
	@echo "🖥️ Backend詳細コマンド（統合済み）:"
	@echo "  make shell               - Django shell起動"
	@echo "  make migrate             - マイグレーション実行"
	@echo "  make makemigrations       - マイグレーション作成"
	@echo "  make reset-db            - DB完全リセット（警告あり）"
	@echo "  make backup              - DBバックアップ作成"
	@echo "  make test                - テスト実行"

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
	@echo "[MOBILE] iOS詳細コマンド:"
	@echo "  cd ../knest-ios-app && open KnestApp.xcodeproj"
	@echo "  # Xcode で Command+R"
	@echo ""
	@echo "[DATA] KnestApp プロジェクト状態"
	@echo ""
	@echo "Backend:"
	@if [ -f "db.sqlite3" ]; then \
		echo "  [COMPLETE] Database: 存在"; \
	else \
		echo "  [ERROR] Database: 未作成 (make migrate が必要)"; \
	fi
	@if [ -d "$(VENV)" ]; then \
		echo "  [COMPLETE] Virtual Env: 存在"; \
	else \
		echo "  [ERROR] Virtual Env: 未作成 (make setup が必要)"; \
	fi
	@if pgrep -f "python.*manage.py.*runserver" > /dev/null; then \
		echo "  [COMPLETE] Server: 稼働中"; \
	else \
		echo "  [ERROR] Server: 停止中 (make dev で起動)"; \
	fi
	@echo "[MOBILE] iOS状態:"
	@if [ -d "../knest-ios-app/KnestApp.xcodeproj" ]; then \
		echo "  [COMPLETE] Project: 存在"; \
	else \
		echo "  [ERROR] Project: 未作成"; \
	fi
	@if pgrep -f "Simulator" > /dev/null; then \
		echo "  [COMPLETE] Simulator: 稼働中"; \
	else \
		echo "  [STOP] Simulator: 停止中"; \
	fi

# 高速セットアップ（並列処理）
setup-fast:
	@echo "[ROCKET] 高速セットアップを開始します..."
	@$(MAKE) setup
	@echo "[TOOLS] 仮想環境を有効化して依存パッケージをインストールしています..."
	@. $(VENV)/bin/activate && \
	pip install --upgrade pip && \
	pip install -r requirements.txt
	@echo "[COMPLETE] セットアップ完了！'make createsuperuser' で管理者ユーザーを作成してください"

# 高速初期データ作成（並列処理）
create-sample-data-fast: check-venv
	@echo "[ROCKET] 高速初期データ作成を開始します..."
	@echo "[SPEED] 並列処理で実行中..."
	@. $(VENV)/bin/activate && ( \
		$(PYTHON) create_sample_data.py & \
		$(PYTHON) create_initial_tags.py & \
		$(PYTHON) create_hierarchical_sample_data.py & \
		wait \
	)
	@echo "[COMPLETE] 高速初期データ作成完了！"

# データベースマイグレーション（高速版）
migrate: check-venv
	@echo "🗃️ Applying migrations..."
	@. $(VENV)/bin/activate && $(MANAGE) migrate --verbosity=1

# 高速テスト実行
test-fast: check-venv
	@. $(VENV)/bin/activate && $(MANAGE) test --parallel --keepdb

# 高速クリーンアップ
clean-fast:
	@echo "🧹 高速クリーンアップ中..."
	rm -rf venv/ &
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null &
	find . -type f -name "*.pyc" -delete &
	wait
	@echo "✅ クリーンアップ完了！" 