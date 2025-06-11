# API エンドポイント一覧

## 認証関連

### ユーザー認証
- `POST /api/auth/login/` - ログイン
- `POST /api/auth/logout/` - ログアウト
- `POST /api/auth/register/` - ユーザー登録
- `POST /api/auth/password/reset/` - パスワードリセット
- `POST /api/auth/password/change/` - パスワード変更

## ユーザー関連

### プロフィール
- `GET /api/users/me/` - 自分のプロフィール取得
- `PUT /api/users/me/` - プロフィール更新
- `PATCH /api/users/me/emotion/` - 感情状態更新

### 興味管理
- `GET /api/interests/` - 興味一覧取得
- `POST /api/interests/` - 興味作成（プレミアム会員のみ）
- `GET /api/interests/{id}/` - 興味詳細取得
- `PUT /api/interests/{id}/` - 興味更新（作成者のみ）
- `DELETE /api/interests/{id}/` - 興味削除（作成者のみ）

### ユーザーの興味
- `GET /api/users/me/interests/` - 自分の興味一覧
- `POST /api/users/me/interests/` - 興味追加
- `PUT /api/users/me/interests/{id}/` - 興味の強さ更新
- `DELETE /api/users/me/interests/{id}/` - 興味削除

## AIサポート関連

### セッション管理
- `GET /api/ai-support/sessions/` - セッション一覧
- `POST /api/ai-support/sessions/` - 新規セッション作成
- `GET /api/ai-support/sessions/{id}/` - セッション詳細
- `PATCH /api/ai-support/sessions/{id}/` - セッション更新
- `DELETE /api/ai-support/sessions/{id}/` - セッション削除

### メッセージ
- `GET /api/ai-support/sessions/{id}/messages/` - メッセージ一覧
- `POST /api/ai-support/sessions/{id}/messages/` - メッセージ送信
- `PUT /api/ai-support/sessions/{id}/messages/{message_id}/` - メッセージ更新
- `DELETE /api/ai-support/sessions/{id}/messages/{message_id}/` - メッセージ削除

## サブスクリプション関連

### プラン管理
- `GET /api/subscriptions/plans/` - プラン一覧
- `GET /api/subscriptions/my-plan/` - 現在のプラン情報

### サブスクリプション
- `POST /api/subscriptions/subscribe/` - サブスクリプション開始
- `POST /api/subscriptions/cancel/` - サブスクリプション解約
- `POST /api/subscriptions/renew/` - サブスクリプション更新

### 支払い
- `GET /api/subscriptions/payments/` - 支払い履歴
- `POST /api/subscriptions/payments/process/` - 支払い処理

## メッセージング関連

### メッセージ
- `GET /api/messages/` - メッセージ一覧
- `POST /api/messages/` - メッセージ送信
- `GET /api/messages/{id}/` - メッセージ詳細
- `PUT /api/messages/{id}/` - メッセージ更新
- `DELETE /api/messages/{id}/` - メッセージ削除

### リアクション
- `POST /api/messages/{id}/reactions/` - リアクション追加
- `DELETE /api/messages/{id}/reactions/{reaction_id}/` - リアクション削除

## レスポンス形式

### 成功レスポンス
```json
{
    "status": "success",
    "data": {
        // レスポンスデータ
    }
}
```

### エラーレスポンス
```json
{
    "status": "error",
    "code": "ERROR_CODE",
    "message": "エラーメッセージ",
    "details": {
        // 詳細なエラー情報
    }
}
```

## 認証

- すべてのAPIエンドポイントは、`Authorization`ヘッダーにJWTトークンが必要
- 例: `Authorization: Bearer <token>`

## レート制限

- 認証済みユーザー: 1000リクエスト/時
- 未認証ユーザー: 100リクエスト/時
- プレミアムユーザー: 5000リクエスト/時 