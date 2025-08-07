from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from django.utils import timezone
from datetime import timedelta
import logging

from .serializers import (
    CustomTokenObtainPairSerializer,
    UserRegistrationSerializer,
    UserProfileSerializer,
    PasswordChangeSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer
)

User = get_user_model()
logger = logging.getLogger(__name__)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer
    
    def create(self, request, *args, **kwargs):
        logger.debug(f"Registration request data: {request.data}")
        
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"Registration validation errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user = serializer.save()
        logger.info(f"User {user.username} registered successfully")
        
        # レスポンスにトークンも含める
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': str(user.id),
                'username': user.username,
                'email': user.email,
                'display_name': user.display_name,
                'avatar_url': user.avatar_url or '',
                'bio': user.bio or '',
                'emotion_state': user.emotion_state or '',
                'birth_date': user.birth_date.isoformat() if user.birth_date else None,
                'prefecture': user.prefecture,
                'is_premium': user.is_premium,
                'last_active': user.last_active.isoformat() if user.last_active else None,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'updated_at': user.updated_at.isoformat() if user.updated_at else None
            }
        }, status=status.HTTP_201_CREATED)

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JWTAuthentication]

    def get_object(self):
        return self.request.user

class PasswordChangeView(generics.GenericAPIView):
    serializer_class = PasswordChangeSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JWTAuthentication]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response(
                {"old_password": "現在のパスワードが正しくありません。"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({"message": "パスワードが変更されました。"})

class PasswordResetRequestView(generics.CreateAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
            token = get_random_string(64)
            user.password_reset_token = token
            user.password_reset_token_created = timezone.now()
            user.save(update_fields=['password_reset_token', 'password_reset_token_created'])

            reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
            send_mail(
                '【Knest】パスワードリセット',
                f'以下のURLからパスワードをリセットしてください：\n\n{reset_url}\n\n'
                'このリンクは24時間有効です。',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
        except User.DoesNotExist:
            pass

        return Response({"message": "パスワードリセット手順をメールで送信しました。"})

class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data['token']
        try:
            user = User.objects.get(
                password_reset_token=token,
                password_reset_token_created__gt=timezone.now() - timedelta(days=1)
            )
            user.set_password(serializer.validated_data['new_password'])
            user.password_reset_token = None
            user.password_reset_token_created = None
            user.save()
            return Response({"message": "パスワードがリセットされました。"})
        except User.DoesNotExist:
            return Response(
                {"token": "無効または期限切れのトークンです。"},
                status=status.HTTP_400_BAD_REQUEST
            )

class TestUserLoginView(generics.CreateAPIView):
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        try:
            # テストユーザーを取得または作成
            test_user, created = User.objects.get_or_create(
                username='testuser',
                defaults={
                    'email': 'test@example.com',
                    'display_name': 'テストユーザー',
                    'is_active': True
                }
            )
            
            if created:
                test_user.set_password('testpass123')
                test_user.save()
            
            # JWTトークンを生成
            from rest_framework_simplejwt.tokens import RefreshToken
            refresh = RefreshToken.for_user(test_user)
            
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': str(test_user.id),
                    'username': test_user.username,
                    'email': test_user.email,
                    'display_name': test_user.display_name,
                    'avatar_url': test_user.avatar_url or '',
                    'bio': test_user.bio or '',
                    'emotion_state': test_user.emotion_state or '',
                    'is_premium': test_user.is_premium,
                    'last_active': test_user.last_active.isoformat(),
                    'created_at': test_user.created_at.isoformat(),
                    'updated_at': test_user.updated_at.isoformat()
                }
            })
            
        except Exception as e:
            logger.error(f"Error in test user login: {str(e)}")
            return Response(
                {"error": "テストユーザーログインに失敗しました"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) 