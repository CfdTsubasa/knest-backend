# Knest API Documentation

## 概要
KnestアプリケーションのバックエンドAPIドキュメント

## 認証
すべてのAPIエンドポイントは認証が必要です。

### 認証ヘッダー
```
Authorization: Bearer {token}
```

## エンドポイント

### サークル関連 API

#### サークル一覧の取得
```http
GET /api/circles/circles/
```

**クエリパラメータ:**
- `category`: カテゴリーID（複数指定可）
- `min_members`: 最小メンバー数
- `max_members`: 最大メンバー数
- `search`: 検索キーワード
- `ordering`: ソート順（created_at, member_count, post_count, last_activity）

**レスポンス例:**
```json
{
    "count": 10,
    "next": "http://api.example.com/circles/?page=2",
    "previous": null,
    "results": [
        {
            "id": "uuid",
            "name": "サークル名",
            "description": "説明",
            "icon_url": "https://example.com/icon.jpg",
            "cover_url": "https://example.com/cover.jpg",
            "categories": [],
            "tags": [],
            "member_count": 5,
            "post_count": 10,
            "last_activity": "2024-03-14T12:00:00Z",
            "rules": "サークル規約"
        }
    ]
}
```

#### サークルの作成
```http
POST /api/circles/circles/
```

**リクエストボディ:**
```json
{
    "name": "サークル名",
    "description": "説明",
    "icon_url": "https://example.com/icon.jpg",
    "cover_url": "https://example.com/cover.jpg",
    "categories": ["category_id1", "category_id2"],
    "tags": ["タグ1", "タグ2"],
    "rules": "サークル規約"
}
```

#### サークルへの参加
```http
POST /api/circles/circles/{circle_id}/join/
```

#### サークルからの退会
```http
POST /api/circles/circles/{circle_id}/leave/
```

### チャット関連 API

#### メッセージ一覧の取得
```http
GET /api/circles/chats/?circle={circle_id}
```

**レスポンス例:**
```json
{
    "count": 50,
    "next": "http://api.example.com/chats/?circle=uuid&cursor=xxx",
    "previous": null,
    "results": [
        {
            "id": "uuid",
            "circle": "circle_id",
            "sender": {
                "id": "user_id",
                "username": "username",
                "display_name": "表示名",
                "avatar_url": "https://example.com/avatar.jpg"
            },
            "content": "メッセージ内容",
            "media_urls": [],
            "created_at": "2024-03-14T12:00:00Z",
            "is_system_message": false,
            "is_edited": false,
            "reply_to": null,
            "read_by": [
                {
                    "id": "user_id",
                    "username": "username",
                    "display_name": "表示名"
                }
            ]
        }
    ]
}
```

#### 未読メッセージ数の取得
```http
GET /api/circles/chats/unread_count/?circle={circle_id}
```

**レスポンス例:**
```json
{
    "unread_count": 5
}
```

### WebSocket API

#### チャット接続
```
ws://example.com/ws/circle/{circle_id}/chat/
```

**送信可能なメッセージタイプ:**

1. メッセージ送信
```json
{
    "type": "message",
    "content": "メッセージ内容",
    "reply_to": "返信先メッセージID（オプション）"
}
```

2. タイピング通知
```json
{
    "type": "typing"
}
```

3. 既読通知
```json
{
    "type": "read"
}
```

**受信するメッセージタイプ:**

1. 新規メッセージ
```json
{
    "type": "message",
    "message": {
        "id": "uuid",
        "content": "メッセージ内容",
        "sender": {
            "id": "user_id",
            "username": "username",
            "display_name": "表示名",
            "avatar_url": "https://example.com/avatar.jpg"
        },
        "created_at": "2024-03-14T12:00:00Z",
        "is_system_message": false,
        "reply_to": null
    }
}
```

2. タイピング通知
```json
{
    "type": "typing",
    "user": {
        "id": "user_id",
        "username": "username",
        "display_name": "表示名"
    }
}
```

3. 既読通知
```json
{
    "type": "read",
    "user": {
        "id": "user_id",
        "username": "username",
        "display_name": "表示名"
    }
}
```

4. オンライン状態通知
```json
{
    "type": "online",
    "user": {
        "id": "user_id",
        "username": "username",
        "display_name": "表示名"
    }
}
```

5. オフライン状態通知
```json
{
    "type": "offline",
    "user": {
        "id": "user_id",
        "username": "username",
        "display_name": "表示名"
    }
}
```

## 制限事項

### サークル関連
- 1ユーザーが作成できるサークル数: 2（プレミアムユーザーは4）
- 1ユーザーが参加できるサークル数: 2（プレミアムユーザーは4）
- サークルの最大メンバー数: 10名

### チャット関連
- メッセージの取得: 1回のリクエストで最大50件
- メディアファイルの制限: 未実装（今後実装予定）

## エラーレスポンス

```json
{
    "detail": "エラーメッセージ"
}
```

主なエラーケース：
- 401: 認証エラー
- 403: 権限エラー
- 404: リソースが見つからない
- 400: リクエストが不正 