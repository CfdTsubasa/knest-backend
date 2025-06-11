from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q, Count
from django_filters import rest_framework as django_filters
from django.utils.translation import gettext_lazy as _
from .models import Category, Circle, CircleMembership, CirclePost, CircleEvent, CircleChat, CircleChatRead
from .serializers import (
    CategorySerializer,
    CircleSerializer,
    CircleMembershipSerializer,
    CircleJoinRequestSerializer,
    CircleJoinResponseSerializer,
    CirclePostSerializer,
    CircleEventSerializer,
    CircleChatSerializer
)
from .permissions import IsCircleOwnerOrAdmin, CanJoinCircle
from .filters import CircleFilter
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.core.cache import cache
from django.conf import settings
from django.db import transaction
from rest_framework.pagination import CursorPagination
from .recommendation import get_personalized_recommendations, get_trending_circles

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """カテゴリーのビューセット"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

class CircleViewSet(viewsets.ModelViewSet):
    """サークルのビューセット"""
    serializer_class = CircleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'tags']
    ordering_fields = ['created_at', 'member_count', 'post_count', 'last_activity']
    ordering = ['-last_activity']

    def get_queryset(self):
        queryset = Circle.objects.all()
        
        # カテゴリーでフィルタリング
        categories = self.request.query_params.getlist('category')
        if categories:
            queryset = queryset.filter(categories__id__in=categories)

        # メンバー数でフィルタリング
        min_members = self.request.query_params.get('min_members')
        max_members = self.request.query_params.get('max_members')
        if min_members:
            queryset = queryset.filter(member_count__gte=min_members)
        if max_members:
            queryset = queryset.filter(member_count__lte=max_members)

        return queryset.distinct()

    def perform_create(self, serializer):
        # ユーザーの作成可能サークル数をチェック
        user_circles = Circle.objects.filter(
            memberships__user=self.request.user
        ).count()
        max_circles = 4 if self.request.user.is_premium else 2
        
        if user_circles >= max_circles:
            raise serializers.ValidationError(
                _('作成可能なサークル数の上限に達しています。')
            )
        
        circle = serializer.save()
        
        # 作成者をメンバーとして追加
        CircleMembership.objects.create(
            user=self.request.user,
            circle=circle
        )

    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """サークルに参加"""
        circle = self.get_object()
        
        # 既に参加しているかチェック
        if CircleMembership.objects.filter(
            user=request.user,
            circle=circle
        ).exists():
            return Response(
                {'detail': _('既にサークルに参加しています。')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # メンバー数上限チェック
        if circle.member_count >= 10:
            return Response(
                {'detail': _('サークルのメンバー数が上限に達しています。')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # ユーザーの参加可能サークル数チェック
        user_circles = CircleMembership.objects.filter(
            user=request.user
        ).count()
        max_circles = 4 if request.user.is_premium else 2
        
        if user_circles >= max_circles:
            return Response(
                {'detail': _('参加可能なサークル数の上限に達しています。')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # サークルに参加
        CircleMembership.objects.create(
            user=request.user,
            circle=circle
        )
        circle.member_count += 1
        circle.save()
        
        return Response(status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        """サークルから退会"""
        circle = self.get_object()
        
        try:
            membership = CircleMembership.objects.get(
                user=request.user,
                circle=circle
            )
            membership.delete()
            
            circle.member_count -= 1
            circle.save()
            
            return Response(status=status.HTTP_204_NO_CONTENT)
        except CircleMembership.DoesNotExist:
            return Response(
                {'detail': _('サークルに参加していません。')},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def respond_to_request(self, request, pk=None):
        """参加申請への応答（承認/拒否）"""
        circle = self.get_object()
        if not IsCircleOwnerOrAdmin().has_object_permission(request, self, circle):
            return Response(
                {'detail': '権限がありません。'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = CircleJoinResponseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        membership_id = request.data.get('membership_id')
        try:
            membership = CircleMembership.objects.get(
                circle=circle,
                id=membership_id,
                status='pending'
            )
        except CircleMembership.DoesNotExist:
            return Response(
                {'detail': '申請が見つかりません。'},
                status=status.HTTP_404_NOT_FOUND
            )

        if serializer.validated_data['action'] == 'approve':
            membership.status = 'active'
            membership.joined_at = timezone.now()
        else:
            membership.status = 'rejected'
            membership.rejection_reason = serializer.validated_data.get('rejection_reason', '')

        membership.save()
        return Response(CircleMembershipSerializer(membership).data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my(self, request):
        """
        ユーザーが参加中のサークル一覧を取得
        """
        # ユーザーが参加中のサークルを取得
        my_circles = Circle.objects.filter(
            memberships__user=request.user,
            memberships__status='active'
        ).distinct().order_by('-memberships__joined_at')
        
        serializer = self.get_serializer(my_circles, many=True)
        return Response({
            'count': len(my_circles),
            'results': serializer.data
        })

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def recommended(self, request):
        """
        パーソナライズド推薦サークルを取得
        
        Query Parameters:
        - algorithm: 'simple', 'weighted', 'collaborative', 'hybrid' (default: 'hybrid')
        - limit: 結果数制限 (default: 10)
        """
        algorithm = request.query_params.get('algorithm', 'hybrid')
        limit = int(request.query_params.get('limit', 10))
        
        recommended_circles = get_personalized_recommendations(
            user=request.user,
            algorithm=algorithm,
            limit=limit
        )
        
        serializer = self.get_serializer(recommended_circles, many=True)
        return Response({
            'algorithm_used': algorithm,
            'count': len(recommended_circles),
            'results': serializer.data
        })

    @action(detail=False, methods=['get'])
    def trending(self, request):
        """
        トレンドサークルを取得
        """
        limit = int(request.query_params.get('limit', 10))
        trending_circles = get_trending_circles(limit=limit)
        
        serializer = self.get_serializer(trending_circles, many=True)
        return Response({
            'count': len(trending_circles),
            'results': serializer.data
        })

class CircleMembershipViewSet(viewsets.ReadOnlyModelViewSet):
    """サークルメンバーシップのビューセット"""
    serializer_class = CircleMembershipSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CircleMembership.objects.filter(
            Q(user=self.request.user) |
            Q(circle__memberships__user=self.request.user,
              circle__memberships__status='active')
        )

class CirclePostViewSet(viewsets.ModelViewSet):
    """サークル投稿のビューセット"""
    serializer_class = CirclePostSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return CirclePost.objects.filter(
            circle__memberships__user=self.request.user
        ).select_related('author', 'circle')
    
    def perform_create(self, serializer):
        circle = serializer.validated_data['circle']
        
        # メンバーかどうかチェック
        if not CircleMembership.objects.filter(
            user=self.request.user,
            circle=circle
        ).exists():
            raise serializers.ValidationError(
                _('サークルのメンバーではありません。')
            )
        
        serializer.save(author=self.request.user)
        
        # 投稿数を更新
        circle.post_count += 1
        circle.save()

class CircleEventViewSet(viewsets.ModelViewSet):
    """サークルイベントのビューセット"""
    serializer_class = CircleEventSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return CircleEvent.objects.filter(
            circle__memberships__user=self.request.user
        ).select_related('circle')
    
    def perform_create(self, serializer):
        circle = serializer.validated_data['circle']
        
        # メンバーかどうかチェック
        if not CircleMembership.objects.filter(
            user=self.request.user,
            circle=circle
        ).exists():
            raise serializers.ValidationError(
                _('サークルのメンバーではありません。')
            ) 

class ChatMessagePagination(CursorPagination):
    """チャットメッセージのページネーション"""
    page_size = 50
    ordering = 'created_at'
    cursor_query_param = 'cursor'

class CircleChatViewSet(viewsets.ModelViewSet):
    """サークルチャットのビューセット"""
    serializer_class = CircleChatSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ChatMessagePagination
    ordering = ['created_at']
    
    def get_queryset(self):
        circle_id = self.request.query_params.get('circle')
        if not circle_id:
            return CircleChat.objects.none()

        # サークルのメンバーかどうかチェック
        if not CircleMembership.objects.filter(
            user=self.request.user,
            circle_id=circle_id,
            status='active'
        ).exists():
            raise PermissionDenied(_('このサークルのメンバーではありません。'))

        # キャッシュキーの生成
        cache_key = f'circle_chat_{circle_id}_messages'
        
        # 🔧 キャッシュを一時的に無効化
        # cached_messages = cache.get(cache_key)
        # if cached_messages is not None:
        #     return cached_messages

        # DBからメッセージを取得
        queryset = CircleChat.objects.filter(circle_id=circle_id).select_related(
            'sender',
            'reply_to',
            'reply_to__sender'
        ).order_by('created_at')

        print(f"🔍 クエリセット取得: circle_id={circle_id}, count={queryset.count()}")

        # キャッシュに保存（一時的にコメントアウト）
        # cache.set(
        #     cache_key,
        #     queryset,
        #     timeout=settings.CHAT_MESSAGE_CACHE_TIMEOUT
        # )

        # 非同期で既読を更新
        transaction.on_commit(lambda: self._update_read_status(
            self.request.user.id,
            circle_id
        ))

        return queryset

    @staticmethod
    def _update_read_status(user_id, circle_id):
        """既読ステータスを更新（非同期）"""
        CircleChatRead.objects.update_or_create(
            user_id=user_id,
            circle_id=circle_id,
            defaults={'last_read': timezone.now()}
        )

    def perform_create(self, serializer):
        circle = serializer.validated_data['circle']
        
        # メンバーかどうかチェック
        if not CircleMembership.objects.filter(
            user=self.request.user,
            circle=circle,
            status='active'
        ).exists():
            raise PermissionDenied(_('このサークルのメンバーではありません。'))
        
        # 返信先のメッセージが同じサークルのものかチェック
        reply_to = self.request.data.get('reply_to')
        if reply_to:
            try:
                reply_message = CircleChat.objects.get(id=reply_to)
                if reply_message.circle_id != circle.id:
                    raise ValidationError(_('異なるサークルのメッセージには返信できません。'))
                serializer.validated_data['reply_to'] = reply_message
            except CircleChat.DoesNotExist:
                raise ValidationError(_('返信先のメッセージが見つかりません。'))
        
        # メッセージを保存
        message = serializer.save(sender=self.request.user)
        
        print(f"💾 メッセージ保存成功: content='{message.content}', circle={message.circle.name}")
        
        # キャッシュを削除（次のリクエストで再生成）
        cache_key = f'circle_chat_{circle.id}_messages'
        cache.delete(cache_key)
        print(f"🗑️ キャッシュ削除: {cache_key}")
        
        return message

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """未読メッセージ数を取得"""
        circle_id = request.query_params.get('circle')
        
        if circle_id:
            # キャッシュキーの生成
            cache_key = f'circle_chat_{circle_id}_unread_{request.user.id}'
            
            # キャッシュから未読数を取得
            unread_count = cache.get(cache_key)
            if unread_count is not None:
                return Response({'unread_count': unread_count})
            
            # DBから未読数を取得
            try:
                last_read = CircleChatRead.objects.get(
                    user=request.user,
                    circle_id=circle_id
                ).last_read
            except CircleChatRead.DoesNotExist:
                last_read = request.user.date_joined
            
            unread_count = CircleChat.objects.filter(
                circle_id=circle_id,
                created_at__gt=last_read
            ).exclude(sender=request.user).count()
            
            # キャッシュに保存
            cache.set(
                cache_key,
                unread_count,
                timeout=settings.CHAT_UNREAD_COUNT_CACHE_TIMEOUT
            )
            
            return Response({'unread_count': unread_count})
        else:
            # キャッシュキーの生成
            cache_key = f'circle_chat_all_unread_{request.user.id}'
            
            # キャッシュから未読数を取得
            unread_counts = cache.get(cache_key)
            if unread_counts is not None:
                return Response(unread_counts)
            
            # DBから未読数を取得
            unread_counts = {}
            for membership in CircleMembership.objects.filter(
                user=request.user,
                status='active'
            ).select_related('circle'):
                try:
                    last_read = CircleChatRead.objects.get(
                        user=request.user,
                        circle=membership.circle
                    ).last_read
                except CircleChatRead.DoesNotExist:
                    last_read = request.user.date_joined
                
                unread_count = CircleChat.objects.filter(
                    circle=membership.circle,
                    created_at__gt=last_read
                ).exclude(sender=request.user).count()
                
                if unread_count > 0:
                    unread_counts[str(membership.circle.id)] = unread_count
            
            # キャッシュに保存
            cache.set(
                cache_key,
                unread_counts,
                timeout=settings.CHAT_UNREAD_COUNT_CACHE_TIMEOUT
            )
            
            return Response(unread_counts) 