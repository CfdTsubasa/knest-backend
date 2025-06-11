from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch
from django.utils import timezone
from .factories import UserFactory, AISupportSessionFactory, AISupportMessageFactory

class AISupportSessionViewSetTests(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)

    def test_create_session(self):
        """新しいセッションを作成できることをテスト"""
        url = reverse('ai_support:session-list')
        data = {
            'title': 'テストセッション',
            'description': 'テストの説明'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'テストセッション')
        self.assertEqual(response.data['status'], 'active')

    def test_list_sessions(self):
        """セッション一覧を取得できることをテスト"""
        sessions = [
            AISupportSessionFactory(user=self.user)
            for _ in range(3)
        ]
        url = reverse('ai_support:session-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)

    def test_complete_session(self):
        """セッションを完了できることをテスト"""
        session = AISupportSessionFactory(user=self.user)
        url = reverse('ai_support:session-complete', args=[session.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'completed')

class AISupportMessageViewSetTests(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.session = AISupportSessionFactory(user=self.user)
        self.client.force_authenticate(user=self.user)

    @patch('knest_backend.apps.ai_support.services.AIChatService.get_chat_response')
    def test_create_message(self, mock_get_chat_response):
        """新しいメッセージを作成できることをテスト"""
        mock_get_chat_response.return_value = "AIの応答テスト"
        
        url = reverse('ai_support:message-list', args=[self.session.id])
        data = {
            'content': 'ユーザーメッセージテスト'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user_message']['content'], 'ユーザーメッセージテスト')
        self.assertEqual(response.data['ai_message']['content'], 'AIの応答テスト')

    def test_list_messages(self):
        """メッセージ一覧を取得できることをテスト"""
        messages = [
            AISupportMessageFactory(session=self.session)
            for _ in range(3)
        ]
        url = reverse('ai_support:message-list', args=[self.session.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)

    def test_unauthorized_access(self):
        """他のユーザーのセッションにアクセスできないことをテスト"""
        other_user = UserFactory()
        other_session = AISupportSessionFactory(user=other_user)
        url = reverse('ai_support:message-list', args=[other_session.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN) 