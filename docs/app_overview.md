# Knestアプリケーション概要

## アプリケーション構成

Knestは以下のDjangoアプリケーションで構成されています：

1. `users` - ユーザー管理
2. `interests` - 興味・関心管理
3. `ai_support` - AIサポート機能
4. `subscriptions` - サブスクリプション管理
5. `chat_messages` - メッセージ管理
6. `reactions` - リアクション管理

## モデル詳細

### Users App

#### User (カスタムユーザーモデル)
- `id`: UUID - プライマリーキー
- `display_name`: 表示名
- `avatar_url`: アバターURL
- `bio`: 自己紹介
- `emotion_state`: 現在の気分
- `is_premium`: プレミアム会員フラグ
- `last_active`: 最終アクティブ時間
- `created_at`: 作成日時
- `updated_at`: 更新日時

### Interests App

#### Interest (興味モデル)
- `id`: UUID - プライマリーキー
- `name`: 興味の名前（ユニーク）
- `description`: 説明
- `category`: カテゴリー（趣味、ライフスタイル、感情、スキル）
- `is_official`: 公式フラグ
- `creator`: 作成者（User）
- `usage_count`: 使用回数
- `icon_url`: アイコンURL
- `created_at`: 作成日時
- `updated_at`: 更新日時

#### UserInterest (ユーザーの興味モデル)
- `id`: UUID - プライマリーキー
- `user`: ユーザー（User）
- `interest`: 興味（Interest）
- `intensity`: 興味の強さ（1-5）
- `added_at`: 追加日時

### AI Support App

#### AISupportSession (AIサポートセッション)
- `id`: UUID - プライマリーキー
- `user`: ユーザー（User）
- `title`: セッションタイトル
- `description`: セッション説明
- `status`: ステータス（進行中、完了、キャンセル）
- `started_at`: 開始日時
- `completed_at`: 完了日時
- `last_interaction_at`: 最終インタラクション日時

#### AISupportMessage (AIサポートメッセージ)
- `id`: UUID - プライマリーキー
- `session`: セッション（AISupportSession）
- `message_type`: メッセージタイプ（ユーザー、AI）
- `content`: メッセージ内容
- `created_at`: 作成日時

### Subscriptions App

#### Subscription (サブスクリプション)
- `id`: UUID - プライマリーキー
- `user`: ユーザー（User）
- `plan`: プラン（無料、ベーシック、プレミアム）
- `status`: ステータス（アクティブ、キャンセル、期限切れ）
- `start_date`: 開始日
- `end_date`: 終了日
- `auto_renew`: 自動更新フラグ
- `created_at`: 作成日時
- `updated_at`: 更新日時

#### Payment (支払い履歴)
- `id`: UUID - プライマリーキー
- `subscription`: サブスクリプション（Subscription）
- `amount`: 金額
- `currency`: 通貨
- `status`: ステータス（処理中、完了、失敗、返金済み）
- `payment_method`: 支払い方法
- `transaction_id`: 取引ID
- `created_at`: 作成日時
- `updated_at`: 更新日時

### Chat Messages App

#### Message (メッセージ)
- `id`: UUID - プライマリーキー
- `circle`: サークル
- `sender`: 送信者（User）
- `content`: メッセージ内容
- `message_type`: メッセージタイプ（テキスト、感情、サポート要請）
- `emotion_tag`: 感情タグ
- `reply_to`: 返信先メッセージ
- `created_at`: 作成日時
- `updated_at`: 更新日時
- `is_edited`: 編集フラグ
- `is_deleted`: 削除フラグ

### Reactions App

#### Reaction (リアクション)
- `id`: UUID - プライマリーキー
- `message`: メッセージ（Message）
- `user`: ユーザー（User）
- `reaction_type`: リアクションタイプ（共感、サポート、ハート、ハグ）
- `created_at`: 作成日時

## 技術スタック

- Python 3.9.6
- Django 4.2.22
- Django REST Framework 3.14.0
- PostgreSQL（開発環境ではSQLite3）
- Redis（キャッシュ、非同期処理）
- Celery（非同期タスク処理）

## 主な機能

1. ユーザー管理
   - カスタムユーザー認証
   - プロフィール管理
   - 感情状態の追跡

2. 興味・関心管理
   - 興味の登録・管理
   - 興味の強さの設定
   - 公式・ユーザー作成興味の区別

3. AIサポート
   - AIとのチャットセッション
   - 感情分析・サポート
   - セッション履歴管理

4. サブスクリプション
   - プラン管理
   - 支払い処理
   - 自動更新管理

5. メッセージング
   - テキストメッセージ
   - 感情表現
   - リアクション機能

## セキュリティ対策

- UUIDを使用したID生成
- パスワードのハッシュ化
- トークンベースの認証
- XSS/CSRF対策
- レート制限の実装 