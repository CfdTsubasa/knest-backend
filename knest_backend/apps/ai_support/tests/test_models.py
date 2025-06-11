from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from .factories import UserFactory, AISupportSessionFactory, AISupportMessageFactory

class AISupportSessionTests(TestCase):
    def setUp(self):
        self.user = UserFactory()

    def test_session_creation(self):
        """セッションが正しく作成されることをテスト"""
        session = AISupportSessionFactory(user=self.user)
        self.assertEqual(session.status, 'active')
        self.assertIsNotNone(session.started_at)
        self.assertIsNone(session.completed_at)

    def test_session_completion(self):
        """セッションが正しく完了することをテスト"""
        session = AISupportSessionFactory(user=self.user)
        session.status = 'completed'
        session.completed_at = timezone.now()
        session.save()
        
        self.assertEqual(session.status, 'completed')
        self.assertIsNotNone(session.completed_at)

    def test_session_timeout(self):
        """セッションのタイムアウトをテスト"""
        session = AISupportSessionFactory(user=self.user)
        # 最終更新時間を設定されたタイムアウト時間より前に設定
        session.last_interaction_at = timezone.now() - timedelta(
            seconds=settings.AI_SUPPORT_SESSION_TIMEOUT + 1
        )
        session.save()
        
        # セッションが自動的に完了状態になることを確認
        self.assertEqual(session.status, 'completed')
        self.assertIsNotNone(session.completed_at)

class AISupportMessageTests(TestCase):
    def setUp(self):
        self.session = AISupportSessionFactory()

    def test_message_creation(self):
        """メッセージが正しく作成されることをテスト"""
        message = AISupportMessageFactory(
            session=self.session,
            message_type='user',
            content='テストメッセージ'
        )
        self.assertEqual(message.message_type, 'user')
        self.assertEqual(message.content, 'テストメッセージ')
        self.assertIsNotNone(message.created_at)

    def test_message_ordering(self):
        """メッセージが作成時間順に並ぶことをテスト"""
        message1 = AISupportMessageFactory(session=self.session)
        message2 = AISupportMessageFactory(session=self.session)
        message3 = AISupportMessageFactory(session=self.session)

        messages = self.session.messages.all()
        self.assertEqual(list(messages), [message1, message2, message3])

    def test_message_types(self):
        """異なるメッセージタイプが正しく扱われることをテスト"""
        user_message = AISupportMessageFactory(
            session=self.session,
            message_type='user'
        )
        ai_message = AISupportMessageFactory(
            session=self.session,
            message_type='ai'
        )

        self.assertEqual(user_message.message_type, 'user')
        self.assertEqual(ai_message.message_type, 'ai') 