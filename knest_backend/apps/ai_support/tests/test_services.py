from django.test import TestCase
from unittest.mock import patch, MagicMock
from ..services import AIChatService
from .factories import AISupportSessionFactory

class AIChatServiceTests(TestCase):
    def setUp(self):
        self.service = AIChatService()
        self.session = AISupportSessionFactory()

    @patch('openai.ChatCompletion.create')
    def test_get_chat_response_success(self, mock_create):
        """AIチャットレスポンスが正しく生成されることをテスト"""
        # OpenAI APIのモックレスポンスを設定
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message={'content': 'AIからのテスト応答'})
        ]
        mock_create.return_value = mock_response

        response = self.service.get_chat_response(
            self.session,
            "ユーザーからのテストメッセージ"
        )

        self.assertEqual(response, 'AIからのテスト応答')
        mock_create.assert_called_once()

    @patch('openai.ChatCompletion.create')
    def test_get_chat_response_with_history(self, mock_create):
        """会話履歴を含めたAIチャットレスポンスが正しく生成されることをテスト"""
        # 事前にメッセージを作成
        self.session.messages.create(
            message_type='user',
            content='以前のユーザーメッセージ'
        )
        self.session.messages.create(
            message_type='ai',
            content='以前のAI応答'
        )

        # OpenAI APIのモックレスポンスを設定
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message={'content': '新しいAI応答'})
        ]
        mock_create.return_value = mock_response

        response = self.service.get_chat_response(
            self.session,
            "新しいユーザーメッセージ"
        )

        self.assertEqual(response, '新しいAI応答')
        # APIが呼び出された際のメッセージ履歴を確認
        call_args = mock_create.call_args[1]
        messages = call_args['messages']
        self.assertEqual(len(messages), 4)  # システムメッセージ + 2つの履歴 + 新しいメッセージ

    @patch('openai.ChatCompletion.create')
    def test_get_chat_response_error(self, mock_create):
        """APIエラー時の処理をテスト"""
        mock_create.side_effect = Exception("APIエラー")

        response = self.service.get_chat_response(
            self.session,
            "テストメッセージ"
        )

        self.assertIn('エラーが発生しました', response)
        self.assertIn('APIエラー', response)

    def test_create_message_pair(self):
        """メッセージペアが正しく作成されることをテスト"""
        with patch.object(self.service, 'get_chat_response') as mock_get_response:
            mock_get_response.return_value = "AIからのテスト応答"

            user_msg, ai_msg = self.service.create_message_pair(
                self.session,
                "ユーザーからのテストメッセージ"
            )

            self.assertEqual(user_msg.message_type, 'user')
            self.assertEqual(user_msg.content, "ユーザーからのテストメッセージ")
            self.assertEqual(ai_msg.message_type, 'ai')
            self.assertEqual(ai_msg.content, "AIからのテスト応答") 