import openai
from django.conf import settings
from .models import AISupportMessage

class AIChatService:
    """
    OpenAI APIを使用してチャット機能を提供するサービスクラス
    """
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        self.max_tokens = settings.OPENAI_MAX_TOKENS
        self.temperature = settings.OPENAI_TEMPERATURE

        # システムメッセージの設定
        self.system_message = {
            "role": "system",
            "content": """あなたは技術的な質問に答えるAIアシスタントです。
以下の原則に従って応答してください：
1. 明確で簡潔な説明を心がける
2. 可能な限り具体例を含める
3. 必要に応じてコードスニペットを提供する
4. セキュリティに関する推奨事項を含める
5. ベストプラクティスに従った解決策を提案する"""
        }

    def get_chat_response(self, session, user_message):
        """
        ユーザーのメッセージに対するAIの応答を生成します
        """
        # セッションの過去のメッセージを取得
        messages = [self.system_message]
        for msg in session.messages.all().order_by('created_at'):
            role = "user" if msg.message_type == "user" else "assistant"
            messages.append({
                "role": role,
                "content": msg.content
            })
        
        # 新しいメッセージを追加
        messages.append({
            "role": "user",
            "content": user_message
        })

        try:
            # OpenAI APIを呼び出し
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            # AIの応答を取得
            ai_response = response.choices[0].message.content

            return ai_response

        except Exception as e:
            # エラーハンドリング
            error_message = f"申し訳ありません。エラーが発生しました: {str(e)}"
            return error_message

    def create_message_pair(self, session, user_message):
        """
        ユーザーメッセージとAI応答のペアを作成します
        """
        # ユーザーメッセージを保存
        user_msg = AISupportMessage.objects.create(
            session=session,
            message_type='user',
            content=user_message
        )

        # AI応答を生成して保存
        ai_response = self.get_chat_response(session, user_message)
        ai_msg = AISupportMessage.objects.create(
            session=session,
            message_type='ai',
            content=ai_response
        )

        return user_msg, ai_msg 