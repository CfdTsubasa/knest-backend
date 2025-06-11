# =============================================================================
# KnestApp Backend Makefile
# =============================================================================

.PHONY: help install setup migrate reset-db server test clean dev prod

# 仮想環境を使用（元のMakefileと整合性を保つ）
VENV := venv
PYTHON := ./$(VENV)/bin/python
PIP := ./$(VENV)/bin/pip
MANAGE := $(PYTHON) manage.py

# ヘルプ表示（デフォルトターゲット）
help:
	@echo "🚀 KnestApp Backend Commands"
	@echo "=============================="
	@echo ""
	@echo "📦 Setup & Installation:"
	@echo "  make install      - 依存関係をインストール (venv内)"
	@echo "  make setup        - 初回セットアップ（DB作成・マイグレーション・スーパーユーザー）"
	@echo ""
	@echo "🗃️  Database:"
	@echo "  make migrate      - マイグレーション実行"
	@echo "  make makemigrations - マイグレーションファイル作成"
	@echo "  make reset-db     - データベースリセット"
	@echo "  make shell        - Django shell起動"
	@echo ""
	@echo "🖥️  Server:"
	@echo "  make server       - 開発サーバー起動"
	@echo "  make server-prod  - 本番サーバー起動"
	@echo ""
	@echo "🧪 Testing & Quality:"
	@echo "  make test         - テスト実行"
	@echo "  make lint         - コード品質チェック"
	@echo "  make format       - コードフォーマット"
	@echo ""
	@echo "🧹 Cleanup:"
	@echo "  make clean        - キャッシュ・一時ファイル削除"
	@echo "  make clean-all    - 完全クリーンアップ"

# 仮想環境チェック
check-venv:
	@if [ ! -d "$(VENV)" ]; then \
		echo "❌ 仮想環境が見つかりません"; \
		echo "💡 ルートディレクトリで 'make setup' を実行してください"; \
		exit 1; \
	fi

# 依存関係インストール
install: check-venv
	@echo "📦 Installing dependencies..."
	$(PIP) install -r requirements.txt

# 初回セットアップ（仮想環境は既に作成済みを前提）
setup: check-venv
	@echo "🚀 Setting up KnestApp Backend..."
	@echo "1️⃣ Creating migrations..."
	$(MANAGE) makemigrations users
	$(MANAGE) makemigrations interests  
	$(MANAGE) makemigrations circles
	@echo "2️⃣ Applying migrations..."
	$(MANAGE) migrate
	@echo "3️⃣ Creating superuser..."
	@echo "Please create a superuser account for admin access:"
	$(MANAGE) createsuperuser
	@echo "✅ Setup complete! You can now run 'make server'"

# マイグレーション関連
makemigrations: check-venv
	@echo "📝 Creating migrations..."
	$(MANAGE) makemigrations

migrate: check-venv
	@echo "🗃️ Applying migrations..."
	$(MANAGE) migrate

# データベースリセット
reset-db: check-venv
	@echo "⚠️  WARNING: This will delete all data!"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ]
	rm -f db.sqlite3
	$(MANAGE) migrate
	@echo "🗃️ Database reset complete!"

# Django shell
shell: check-venv
	@echo "🐍 Starting Django shell..."
	$(MANAGE) shell

# サーバー起動
server: check-venv
	@echo "🖥️ Starting development server..."
	@echo "📱 iOS app should connect to: http://127.0.0.1:8000"
	@echo "🌐 Admin panel: http://127.0.0.1:8000/admin"
	@echo ""
	$(MANAGE) runserver 127.0.0.1:8000

# 本番サーバー
server-prod: check-venv
	@echo "🚀 Starting production server..."
	$(MANAGE) runserver 0.0.0.0:8000

# 静的ファイル収集
collectstatic: check-venv
	@echo "📂 Collecting static files..."
	$(MANAGE) collectstatic --noinput

# テスト実行
test: check-venv
	@echo "🧪 Running tests..."
	$(MANAGE) test

# テストデータ作成
create-test-data: check-venv
	@echo "🎭 Creating test data..."
	$(MANAGE) shell -c "
from apps.users.models import User;
from apps.circles.models import Circle, Category;
from apps.interests.models import Interest;
print('Creating test data...');
# Add your test data creation logic here
print('✅ Test data created!')
"

# コード品質チェック（flake8等が必要）
lint: check-venv
	@echo "🔍 Running code quality checks..."
	@if $(PIP) show flake8 > /dev/null 2>&1; then \
		flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics; \
	else \
		echo "flake8 not installed, skipping..."; \
	fi

# コードフォーマット（black等が必要）
format: check-venv
	@echo "✨ Formatting code..."
	@if $(PIP) show black > /dev/null 2>&1; then \
		black .; \
	else \
		echo "black not installed, skipping..."; \
	fi

# キャッシュ削除
clean:
	@echo "🧹 Cleaning cache files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +

# 完全クリーンアップ
clean-all: clean
	@echo "🧹 Complete cleanup..."
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/

# データベースバックアップ
backup: check-venv
	@echo "💾 Creating database backup..."
	@if [ -f db.sqlite3 ]; then \
		cp db.sqlite3 "db_backup_$(shell date +%Y%m%d_%H%M%S).sqlite3"; \
		echo "✅ Backup created!"; \
	else \
		echo "❌ No database file found"; \
	fi

# 依存関係の更新
update-deps: check-venv
	@echo "📦 Updating dependencies..."
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt --upgrade

# ログ表示
logs:
	@echo "📋 Showing logs..."
	@if [ -f logs/django.log ]; then \
		tail -f logs/django.log; \
	else \
		echo "No log file found"; \
	fi

# API文書生成
docs: check-venv
	@echo "📚 Generating API documentation..."
	@if $(PIP) show django-spectacular > /dev/null 2>&1; then \
		$(MANAGE) spectacular --file schema.yml; \
		echo "✅ API schema generated: schema.yml"; \
	else \
		echo "django-spectacular not installed, skipping..."; \
	fi 