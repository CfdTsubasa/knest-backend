from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q, Count
from django.contrib.auth import get_user_model
from django.db import transaction
from datetime import date, timedelta
import uuid

from .models import (
    Interest, UserInterest, Tag, UserTag,
    InterestCategory, InterestSubcategory, InterestTag, UserInterestProfile
)
from .serializers import (
    InterestSerializer, UserInterestSerializer, TagSerializer, UserTagSerializer,
    InterestCategorySerializer, InterestSubcategorySerializer, InterestTagSerializer, 
    UserInterestProfileSerializer, HierarchicalInterestTreeSerializer,
    UserMatchSerializer, CircleMatchSerializer
)

User = get_user_model()


class InterestViewSet(viewsets.ReadOnlyModelViewSet):
    """
    興味関心の取得用ViewSet
    """
    queryset = Interest.objects.all().order_by('usage_count', 'name')
    serializer_class = InterestSerializer
    permission_classes = [AllowAny]  # 認証不要に変更
    pagination_class = None  # ページネーションを無効化
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # カテゴリでフィルタリング
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)
        
        # 検索クエリ
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """人気の興味関心を取得"""
        popular_interests = self.get_queryset().order_by('-usage_count')[:10]
        serializer = self.get_serializer(popular_interests, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """カテゴリ一覧を取得"""
        categories = Interest.objects.values_list('category', flat=True).distinct()
        return Response(list(categories))


class UserInterestViewSet(viewsets.ModelViewSet):
    """
    ユーザーの興味関心管理用ViewSet
    """
    serializer_class = UserInterestSerializer
    permission_classes = [AllowAny]  # ログイン不要だが、トークンがあれば認証
    pagination_class = None  # ページネーションを無効化
    
    def get_current_user(self):
        """現在のユーザーを取得（ログイン済みまたはtestuser）"""
        # 認証されたユーザーがいる場合はそのユーザーを使用
        if self.request.user.is_authenticated:
            print(f"🔐 認証済みユーザー: {self.request.user.username} (ID: {self.request.user.id})")
            return self.request.user
        
        # 未認証の場合はtestuserを使用
        test_user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
            }
        )
        
        if created:
            test_user.set_password('testpass123')
            test_user.save()
            print(f"✅ testuserを新規作成しました (ID: {test_user.id})")
        else:
            print(f"🧪 開発用testuser: {test_user.username} (ID: {test_user.id})")
        
        return test_user
    
    def get_queryset(self):
        # 現在のユーザー（認証済みまたはtestuser）を取得
        current_user = self.get_current_user()
        user_interests = UserInterest.objects.filter(user=current_user)
        
        print(f"🔍 get_queryset: {current_user.username}の興味数 = {user_interests.count()}")
        for ui in user_interests:
            print(f"  - {ui.interest.name} (ID: {ui.id})")
        
        return user_interests
    
    def create(self, request, *args, **kwargs):
        """カスタム作成処理：重複の場合は既存を返す"""
        
        # 現在のユーザー（認証済みまたはtestuser）を取得
        current_user = self.get_current_user()
        
        # リクエストデータを検証
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # interest_idからinterestオブジェクトを取得
        interest_id = serializer.validated_data['interest_id']
        try:
            interest = Interest.objects.get(id=interest_id)
        except Interest.DoesNotExist:
            return Response(
                {'error': 'Interest not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # トランザクション内で重複チェックと作成を実行
        with transaction.atomic():
            # 重複チェック：既に存在する場合は既存のオブジェクトを返す
            existing_user_interest = UserInterest.objects.filter(
                user=current_user,
                interest=interest
            ).first()
            
            if existing_user_interest:
                # 既存の場合は既存オブジェクトのシリアライザーを作成
                serializer = self.get_serializer(existing_user_interest)
                print(f"🔄 {current_user.username}: 既存の興味を返却 - {existing_user_interest.interest.name}")
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            # 新規作成
            user_interest = UserInterest.objects.create(
                user=current_user,
                interest=interest
            )
            print(f"✅ {current_user.username}: 新規興味を作成 - {user_interest.interest.name} (ID: {user_interest.id})")
        
        serializer = self.get_serializer(user_interest)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def perform_create(self, serializer):
        # createメソッドで処理するため、ここは不要
        pass 


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ハッシュタグ取得用ViewSet（サジェスト用）"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    pagination_class = None
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # 検索クエリでフィルタリング（サジェスト機能）
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        # 使用回数の多い順で最大20件
        return queryset[:20]
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """人気のハッシュタグを取得"""
        popular_tags = self.get_queryset().order_by('-usage_count')[:10]
        serializer = self.get_serializer(popular_tags, many=True)
        return Response(serializer.data)


class UserTagViewSet(viewsets.ModelViewSet):
    """ユーザーハッシュタグ管理用ViewSet"""
    serializer_class = UserTagSerializer
    permission_classes = [AllowAny]
    pagination_class = None
    
    def get_current_user(self):
        """現在のユーザーを取得（ログイン済みまたはtestuser）"""
        
        # 認証されたユーザーがいる場合はそのユーザーを使用
        if self.request.user.is_authenticated:
            print(f"🔐 認証済みユーザー: {self.request.user.username} (ID: {self.request.user.id})")
            return self.request.user
        
        # 未認証の場合はtestuserを使用
        test_user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
            }
        )
        
        if created:
            test_user.set_password('testpass123')
            test_user.save()
            print(f"✅ testuserを新規作成しました (ID: {test_user.id})")
        else:
            print(f"🧪 開発用testuser: {test_user.username} (ID: {test_user.id})")
        
        return test_user
    
    def get_queryset(self):
        current_user = self.get_current_user()
        return UserTag.objects.filter(user=current_user)
    
    def perform_create(self, serializer):
        current_user = self.get_current_user()
        serializer.save(user=current_user)


# ======================================
# 新しい3階層興味関心システム用ViewSet
# ======================================

class InterestCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """興味関心カテゴリViewSet"""
    queryset = InterestCategory.objects.all()
    serializer_class = InterestCategorySerializer
    permission_classes = [AllowAny]
    pagination_class = None


class InterestSubcategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """興味関心サブカテゴリViewSet"""
    queryset = InterestSubcategory.objects.all()
    serializer_class = InterestSubcategorySerializer
    permission_classes = [AllowAny]
    pagination_class = None
    
    def get_queryset(self):
        queryset = super().get_queryset()
        category_id = self.request.query_params.get('category_id')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset


class InterestTagViewSet(viewsets.ReadOnlyModelViewSet):
    """興味関心タグViewSet"""
    queryset = InterestTag.objects.all()
    serializer_class = InterestTagSerializer
    permission_classes = [AllowAny]
    pagination_class = None
    
    def get_queryset(self):
        queryset = super().get_queryset()
        subcategory_id = self.request.query_params.get('subcategory_id')
        if subcategory_id:
            queryset = queryset.filter(subcategory_id=subcategory_id)
        return queryset


class UserInterestProfileViewSet(viewsets.ModelViewSet):
    """ユーザー興味関心プロフィールViewSet"""
    serializer_class = UserInterestProfileSerializer
    permission_classes = [AllowAny]
    pagination_class = None
    
    def get_current_user(self):
        """現在のユーザーを取得"""
        if self.request.user.is_authenticated:
            return self.request.user
        
        # 未認証の場合はtestuserを使用
        test_user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@example.com'}
        )
        return test_user
    
    def get_queryset(self):
        current_user = self.get_current_user()
        return UserInterestProfile.objects.filter(user=current_user)
    
    def perform_create(self, serializer):
        current_user = self.get_current_user()
        serializer.save(user=current_user)


class HierarchicalInterestTreeViewSet(viewsets.ReadOnlyModelViewSet):
    """階層構造ツリー表示ViewSet"""
    queryset = InterestCategory.objects.all()
    serializer_class = HierarchicalInterestTreeSerializer
    permission_classes = [AllowAny]
    pagination_class = None


# ======================================
# マッチングエンジン
# ======================================

class MatchingEngineViewSet(viewsets.ViewSet):
    """マッチングエンジンViewSet"""
    permission_classes = [AllowAny]
    
    def get_current_user(self):
        """現在のユーザーを取得"""
        if self.request.user.is_authenticated:
            return self.request.user
        
        # 未認証の場合はtestuserを使用
        test_user, _ = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@example.com'}
        )
        return test_user
    
    def calculate_matching_score(self, current_user, target_user):
        """マッチングスコアを計算（0.4:0.2:0.4の重み付け）"""
        
        # 1. 興味関心スコア（重み: 0.4）
        current_interests = set(current_user.hierarchical_interests.values_list('tag_id', flat=True))
        target_interests = set(target_user.hierarchical_interests.values_list('tag_id', flat=True))
        
        if current_interests and target_interests:
            common_interests = current_interests & target_interests
            interest_score = len(common_interests) / max(len(current_interests), len(target_interests))
        else:
            interest_score = 0.0
        
        # 2. 居住地スコア（重み: 0.2）
        if current_user.prefecture and target_user.prefecture:
            location_score = 1.0 if current_user.prefecture == target_user.prefecture else 0.5
        else:
            location_score = 0.0
        
        # 3. 年齢スコア（重み: 0.4）
        if current_user.age and target_user.age:
            age_diff = abs(current_user.age - target_user.age)
            if age_diff <= 3:
                age_score = 1.0
            elif age_diff <= 7:
                age_score = 0.7
            elif age_diff <= 15:
                age_score = 0.4
            else:
                age_score = 0.1
        else:
            age_score = 0.0
        
        # 総合スコア計算
        total_score = (interest_score * 0.4) + (location_score * 0.2) + (age_score * 0.4)
        
        # 共通興味関心のタグ名取得
        common_interest_names = []
        if current_interests and target_interests:
            common_tags = InterestTag.objects.filter(id__in=common_interests)
            common_interest_names = [tag.name for tag in common_tags]
        
        return {
            'total_score': round(total_score, 3),
            'interest_score': round(interest_score, 3),
            'location_score': round(location_score, 3),
            'age_score': round(age_score, 3),
            'common_interests': common_interest_names
        }
    
    @action(detail=False, methods=['get'])
    def find_user_matches(self, request):
        """ユーザーマッチングを実行"""
        current_user = self.get_current_user()
        limit = int(request.query_params.get('limit', 20))
        
        # 自分以外のユーザーを取得
        other_users = User.objects.exclude(id=current_user.id)[:50]  # 処理軽量化のため50人に限定
        
        matches = []
        for user in other_users:
            score = self.calculate_matching_score(current_user, user)
            
            # スコアが0.3以上の場合のみマッチ候補とする
            if score['total_score'] >= 0.3:
                match_data = {
                    'id': str(uuid.uuid4()),
                    'user': user,
                    'score': score,
                    'match_reason': f"{len(score['common_interests'])}個の共通点があります"
                }
                matches.append(match_data)
        
        # スコア順でソート
        matches.sort(key=lambda x: x['score']['total_score'], reverse=True)
        matches = matches[:limit]
        
        # シリアライザーで適切な形式に変換
        serializer = UserMatchSerializer(matches, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def find_circle_matches(self, request):
        """サークルマッチングを実行"""
        current_user = self.get_current_user()
        limit = int(request.query_params.get('limit', 20))
        
        # TODO: サークルモデルとの連携が必要
        # 現在はサンプルデータを返す
        sample_matches = []
        return Response(sample_matches)
    
    @action(detail=False, methods=['get'])
    def recommendations(self, request):
        """おすすめユーザー・サークルを取得"""
        return self.find_user_matches(request) 