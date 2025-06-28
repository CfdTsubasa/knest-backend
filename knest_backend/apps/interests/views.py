import uuid
from django.shortcuts import render
from django.db.models import Q, Count
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from django.db import transaction
from datetime import date, timedelta
from .models import (
    Interest, UserInterest, Tag, UserTag,
    InterestCategory, InterestSubcategory, InterestTag, UserInterestProfile
)
from .serializers import (
    InterestSerializer, UserInterestSerializer, TagSerializer, UserTagSerializer,
    InterestCategorySerializer, InterestSubcategorySerializer, InterestTagSerializer,
    UserInterestProfileSerializer, HierarchicalInterestTreeSerializer,
    UserMatchSerializer, CircleMatchSerializer, CreateUserInterestProfileCategoryRequestSerializer,
    CreateUserInterestProfileSubcategoryRequestSerializer
)
from ..users.models import User
from ..circles.models import Circle

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
    permission_classes = [IsAuthenticated]  # 認証必須に変更
    pagination_class = None  # ページネーションを無効化
    
    def get_queryset(self):
        """認証済みユーザーの興味関心のみ取得"""
        return UserInterest.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """興味関心を追加"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 重複チェック
        interest_id = serializer.validated_data['interest'].id
        existing = UserInterest.objects.filter(
            user=self.request.user,
            interest_id=interest_id
        ).first()
        
        if existing:
            # 既に存在する場合は、そのオブジェクトを返す
            return Response(
                UserInterestSerializer(existing).data,
                status=status.HTTP_200_OK
            )
        
        # 新規作成
        serializer.save(user=self.request.user)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )


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
    permission_classes = [IsAuthenticated]  # 認証必須に変更
    pagination_class = None
    
    def get_queryset(self):
        """認証済みユーザーのタグのみ取得"""
        return UserTag.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """認証済みユーザーでタグを作成"""
        serializer.save(user=self.request.user)


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
    permission_classes = [IsAuthenticated]  # 認証必須に変更
    pagination_class = None
    
    def get_queryset(self):
        """認証済みユーザーの興味関心プロフィールのみ取得"""
        return UserInterestProfile.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """認証済みユーザーで興味関心プロフィールを作成"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def add_category_level(self, request):
        """カテゴリレベルで興味関心を追加"""
        serializer = CreateUserInterestProfileCategoryRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        category_id = serializer.validated_data['category_id']
        
        try:
            category = InterestCategory.objects.get(id=category_id)
        except InterestCategory.DoesNotExist:
            return Response(
                {'error': '指定されたカテゴリが見つかりません'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 重複チェック
        existing = UserInterestProfile.objects.filter(
            user=request.user,
            category=category,
            level=1
        ).exists()
        
        if existing:
            return Response(
                {'error': f'「{category.name}」は既に選択されています'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # カテゴリレベルで追加
        profile = UserInterestProfile.objects.create(
            user=request.user,
            category=category,
            level=1
        )
        
        serializer = self.get_serializer(profile)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'])
    def add_subcategory_level(self, request):
        """サブカテゴリレベルで興味関心を追加"""
        serializer = CreateUserInterestProfileSubcategoryRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        category_id = serializer.validated_data['category_id']
        subcategory_id = serializer.validated_data['subcategory_id']
        
        try:
            category = InterestCategory.objects.get(id=category_id)
            subcategory = InterestSubcategory.objects.get(id=subcategory_id, category=category)
        except (InterestCategory.DoesNotExist, InterestSubcategory.DoesNotExist):
            return Response(
                {'error': '指定されたカテゴリまたはサブカテゴリが見つかりません'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 重複チェック
        existing = UserInterestProfile.objects.filter(
            user=request.user,
            subcategory=subcategory,
            level=2
        ).exists()
        
        if existing:
            return Response(
                {'error': f'「{subcategory.name}」は既に選択されています'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # サブカテゴリレベルで追加
        profile = UserInterestProfile.objects.create(
            user=request.user,
            category=category,
            subcategory=subcategory,
            level=2
        )
        
        serializer = self.get_serializer(profile)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


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
    permission_classes = [IsAuthenticated]  # 認証必須に変更
    
    def calculate_matching_score(self, current_user, target_user):
        """マッチングスコアを計算（階層レベルに応じた重み付け）"""
        
        # 1. 興味関心スコア（重み: 0.4）- 階層レベル対応
        interest_score = self._calculate_hierarchical_interest_score(current_user, target_user)
        
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
        total_score = (interest_score['score'] * 0.4) + (location_score * 0.2) + (age_score * 0.4)
        
        return {
            'total_score': round(total_score, 3),
            'interest_score': round(interest_score['score'], 3),
            'location_score': round(location_score, 3),
            'age_score': round(age_score, 3),
            'common_interests': interest_score['common_interests'],
            'hierarchical_details': interest_score['details']
        }
    
    def _calculate_hierarchical_interest_score(self, current_user, target_user):
        """階層レベルに応じた興味関心スコア計算"""
        current_profiles = current_user.hierarchical_interests.all()
        target_profiles = target_user.hierarchical_interests.all()
        
        if not current_profiles or not target_profiles:
            return {
                'score': 0.0,
                'common_interests': [],
                'details': {'exact_matches': 0, 'category_matches': 0, 'subcategory_matches': 0}
            }
        
        # 各レベルでのマッチング計算
        exact_matches = 0      # タグレベル完全一致（重み: 1.0）
        subcategory_matches = 0 # サブカテゴリレベル一致（重み: 0.7）
        category_matches = 0   # カテゴリレベル一致（重み: 0.5）
        
        common_interest_names = []
        
        for current_profile in current_profiles:
            for target_profile in target_profiles:
                # タグレベル完全一致
                if (current_profile.tag_id and target_profile.tag_id and 
                    current_profile.tag_id == target_profile.tag_id):
                    exact_matches += 1
                    if current_profile.tag:
                        common_interest_names.append(f"[TARGET] {current_profile.tag.name}")
                
                # サブカテゴリレベル一致（タグ不一致の場合）
                elif (current_profile.subcategory_id and target_profile.subcategory_id and 
                      current_profile.subcategory_id == target_profile.subcategory_id):
                    subcategory_matches += 1
                    if current_profile.subcategory:
                        common_interest_names.append(f"📂 {current_profile.subcategory.name}")
                
                # カテゴリレベル一致（上位レベル不一致の場合）
                elif (current_profile.category_id and target_profile.category_id and 
                      current_profile.category_id == target_profile.category_id):
                    category_matches += 1
                    if current_profile.category:
                        common_interest_names.append(f"📁 {current_profile.category.name}")
        
        # 重み付けスコア計算
        weighted_score = (exact_matches * 1.0) + (subcategory_matches * 0.7) + (category_matches * 0.5)
        max_possible_score = max(len(current_profiles), len(target_profiles))
        
        # 正規化（0-1の範囲）
        normalized_score = weighted_score / max_possible_score if max_possible_score > 0 else 0.0
        
        return {
            'score': min(normalized_score, 1.0),  # 1.0でキャップ
            'common_interests': list(set(common_interest_names)),  # 重複除去
            'details': {
                'exact_matches': exact_matches,
                'subcategory_matches': subcategory_matches,
                'category_matches': category_matches,
                'weighted_score': round(weighted_score, 2),
                'max_possible_score': max_possible_score
            }
        }
    
    @action(detail=False, methods=['get'])
    def find_user_matches(self, request):
        """ユーザーマッチングを実行"""
        current_user = self.request.user  # 認証済みユーザーを直接使用
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
    
    def _calculate_hierarchical_circle_score(self, current_user, circle):
        """サークルに対する階層レベル重み付けスコア計算"""
        current_profiles = current_user.hierarchical_interests.all()
        
        if not current_profiles:
            return {
                'score': 0.0,
                'common_interests': [],
                'details': {'exact_matches': 0, 'category_matches': 0, 'subcategory_matches': 0}
            }
        
        # サークルの興味関心タグを取得
        circle_tags = getattr(circle, 'interest_tags', [])
        if not circle_tags:
            # フォールバック: tagsフィールドからタグ名で検索
            circle_tag_names = getattr(circle, 'tags', [])
            if circle_tag_names:
                circle_tags = InterestTag.objects.filter(name__in=circle_tag_names)
        
        if not circle_tags:
            return {
                'score': 0.0,
                'common_interests': [],
                'details': {'exact_matches': 0, 'category_matches': 0, 'subcategory_matches': 0}
            }
        
        # 各レベルでのマッチング計算
        exact_matches = 0      # タグレベル完全一致（重み: 1.0）
        subcategory_matches = 0 # サブカテゴリレベル一致（重み: 0.7）
        category_matches = 0   # カテゴリレベル一致（重み: 0.5）
        
        common_interest_names = []
        
        for user_profile in current_profiles:
            for circle_tag in circle_tags:
                # タグレベル完全一致
                if user_profile.tag_id and user_profile.tag_id == circle_tag.id:
                    exact_matches += 1
                    common_interest_names.append(f"[TARGET] {circle_tag.name}")
                
                # サブカテゴリレベル一致（タグ不一致の場合）
                elif (user_profile.subcategory_id and 
                      user_profile.subcategory_id == circle_tag.subcategory_id):
                    subcategory_matches += 1
                    common_interest_names.append(f"📂 {circle_tag.subcategory.name}")
                
                # カテゴリレベル一致（上位レベル不一致の場合）
                elif (user_profile.category_id and 
                      user_profile.category_id == circle_tag.subcategory.category_id):
                    category_matches += 1
                    common_interest_names.append(f"📁 {circle_tag.subcategory.category.name}")
        
        # 重み付けスコア計算
        weighted_score = (exact_matches * 1.0) + (subcategory_matches * 0.7) + (category_matches * 0.5)
        max_possible_score = len(current_profiles)
        
        # 正規化（0-1の範囲）
        normalized_score = weighted_score / max_possible_score if max_possible_score > 0 else 0.0
        
        return {
            'score': min(normalized_score, 1.0),  # 1.0でキャップ
            'common_interests': list(set(common_interest_names)),  # 重複除去
            'details': {
                'exact_matches': exact_matches,
                'subcategory_matches': subcategory_matches,
                'category_matches': category_matches,
                'weighted_score': round(weighted_score, 2),
                'max_possible_score': max_possible_score
            }
        }

    @action(detail=False, methods=['get'])
    def find_circle_matches(self, request):
        """サークルマッチングを実行（階層重み付け対応）"""
        current_user = self.request.user
        limit = int(request.query_params.get('limit', 20))
        algorithm = request.query_params.get('algorithm', 'hierarchical')
        
        try:
            # 階層重み付けアルゴリズムを優先使用
            if algorithm == 'hierarchical':
                return self._hierarchical_circle_matching(current_user, limit)
            
            # 次世代推薦エンジンをフォールバックとして使用
            from ..recommendations.engines import NextGenRecommendationEngine
            engine = NextGenRecommendationEngine(current_user)
            
            # 推薦結果を取得
            recommendations = engine.generate_recommendations(
                algorithm=algorithm,
                limit=limit,
                diversity_factor=0.3
            )
            
            # CircleMatchフォーマットに変換
            circle_matches = []
            for rec in recommendations['recommendations']:
                circle = rec['circle']
                score_data = rec['score']
                reasons = rec['reasons']
                
                # 階層重み付けスコアも計算
                hierarchical_score = self._calculate_hierarchical_circle_score(current_user, circle)
                
                # マッチング理由を日本語で整理
                main_reason = self._format_match_reason(reasons, score_data)
                
                match_data = {
                    'id': str(uuid.uuid4()),
                    'circle': {
                        'id': str(circle.id),
                        'name': circle.name,
                        'description': circle.description,
                        'status': circle.status,
                        'circle_type': circle.circle_type,
                        'member_count': circle.member_count,
                        'post_count': circle.post_count,
                        'tags': circle.tags,
                        'created_at': circle.created_at.isoformat(),
                        'updated_at': circle.updated_at.isoformat(),
                        'last_activity_at': circle.last_activity.isoformat(),
                    },
                    'score': {
                        'total_score': round(max(score_data, hierarchical_score['score']), 3),
                        'interest_score': round(hierarchical_score['score'], 3),
                        'location_score': round(score_data * 0.2, 3),
                        'age_score': round(score_data * 0.1, 3),
                        'common_interests': hierarchical_score['common_interests'],
                        'hierarchical_details': hierarchical_score['details']
                    },
                    'member_count': circle.member_count,
                    'match_reason': main_reason
                }
                circle_matches.append(match_data)
            
            return Response(circle_matches)
            
        except Exception as e:
            print(f"[ERROR] サークルマッチングエラー: {e}")
            # フォールバック: 基本的な推薦システムを使用
            return self._fallback_circle_matching(current_user, limit)
    
    def _hierarchical_circle_matching(self, user, limit):
        """階層重み付けによるサークルマッチング"""
        try:
            # 実際のサークルデータを取得
            from ..circles.models import Circle
            
            print(f"\n🔍 階層マッチング開始:")
            print(f"   ユーザー: {user}")
            print(f"   制限数: {limit}")
            
            # データベースから実際のサークルを取得
            actual_circles = Circle.objects.all()[:20]  # 最大20件
            print(f"   データベースから取得したサークル数: {actual_circles.count()}")
            
            if not actual_circles:
                print(f"   ❌ サークルデータが見つかりません")
                return Response([])
            
            circle_matches = []
            for circle in actual_circles:
                print(f"   📊 処理中: {circle.name} (ID: {circle.id})")
                
                # 階層重み付けスコア計算
                hierarchical_score = self._calculate_hierarchical_circle_score(user, circle)
                print(f"      階層スコア: {hierarchical_score['score']:.3f}")
                
                # スコアが0.1以上の場合のみマッチ候補とする（閾値を下げて含める）
                if hierarchical_score['score'] >= 0.1:
                    # 基本的な位置・年齢スコア（仮実装）
                    location_score = 0.8  # 仮の値
                    age_score = 0.7       # 仮の値
                    
                    # 総合スコア計算（興味40%, 位置20%, 年齢40%）
                    total_score = (hierarchical_score['score'] * 0.4) + (location_score * 0.2) + (age_score * 0.4)
                    
                    match_data = {
                        'id': str(uuid.uuid4()),
                        'circle': {
                            'id': str(circle.id),
                            'name': circle.name,
                            'description': circle.description,
                            'status': circle.status,
                            'circle_type': circle.circle_type,
                            'member_count': circle.member_count,
                            'post_count': circle.post_count,
                            'tags': circle.tags,
                            'created_at': circle.created_at.isoformat(),
                            'updated_at': circle.updated_at.isoformat(),
                            'last_activity_at': circle.last_activity.isoformat(),
                        },
                        'score': {
                            'total_score': round(total_score, 3),
                            'interest_score': round(hierarchical_score['score'], 3),
                            'location_score': round(location_score, 3),
                            'age_score': round(age_score, 3),
                            'common_interests': hierarchical_score['common_interests'],
                            'hierarchical_details': hierarchical_score['details']
                        },
                        'member_count': circle.member_count,
                        'match_reason': self._generate_hierarchical_match_reason(hierarchical_score, total_score)
                    }
                    circle_matches.append(match_data)
                    print(f"      ✅ マッチ候補に追加 (総合スコア: {total_score:.3f})")
                else:
                    print(f"      ❌ スコア不足 ({hierarchical_score['score']:.3f} < 0.1)")
            
            # スコア順でソート
            circle_matches.sort(key=lambda x: x['score']['total_score'], reverse=True)
            result = circle_matches[:limit]
            
            print(f"   ✅ マッチング完了: {len(result)}件のサークルを返します")
            return Response(result)
            
        except Exception as e:
            print(f"❌ 階層マッチングエラー: {e}")
            return Response([])
    
    def _generate_hierarchical_match_reason(self, hierarchical_score, total_score):
        """階層マッチング理由を生成"""
        details = hierarchical_score['details']
        exact = details['exact_matches']
        sub = details['subcategory_matches'] 
        cat = details['category_matches']
        
        if exact > 0:
            return f"🎯 {exact}個の完全一致で{int(total_score * 100)}%マッチ"
        elif sub > 0:
            return f"📂 {sub}個のカテゴリ一致で{int(total_score * 100)}%マッチ"
        elif cat > 0:
            return f"📁 {cat}個の分野一致で{int(total_score * 100)}%マッチ"
        else:
            return f"基本的な適合性で{int(total_score * 100)}%マッチ"
    
    def _format_match_reason(self, reasons, score):
        """マッチング理由を日本語で整理"""
        if not reasons:
            return f"あなたにおすすめのサークルです（適合度: {int(score * 100)}%）"
        
        primary_reason = reasons[0]
        score_percentage = int(score * 100)
        
        if primary_reason['type'] == 'interest_match':
            return f"興味関心が {score_percentage}% マッチしています"
        elif primary_reason['type'] == 'similar_users':
            return f"類似ユーザーが参加中（適合度: {score_percentage}%）"
        elif primary_reason['type'] == 'activity_pattern':
            return f"あなたの活動パターンと一致（適合度: {score_percentage}%）"
        else:
            return f"おすすめのサークルです（適合度: {score_percentage}%）"
    
    def _fallback_circle_matching(self, user, limit):
        """フォールバック用の基本マッチング"""
        from ..circles.recommendation import get_personalized_recommendations
        
        try:
            circles = get_personalized_recommendations(user, algorithm='hybrid', limit=limit)
            
            circle_matches = []
            for i, circle in enumerate(circles):
                # 基本的なスコア計算
                base_score = max(0.3, 1.0 - (i * 0.05))  # 順位に基づく基本スコア
                
                match_data = {
                    'id': str(uuid.uuid4()),
                    'circle': {
                        'id': str(circle.id),
                        'name': circle.name,
                        'description': circle.description,
                        'status': circle.status,
                        'circle_type': circle.circle_type,
                        'member_count': circle.member_count,
                        'post_count': circle.post_count,
                        'tags': circle.tags,
                        'created_at': circle.created_at.isoformat(),
                        'updated_at': circle.updated_at.isoformat(),
                        'last_activity_at': circle.last_activity.isoformat(),
                    },
                    'score': {
                        'total_score': round(base_score, 3),
                        'interest_score': round(base_score * 0.6, 3),
                        'location_score': round(base_score * 0.2, 3),
                        'age_score': round(base_score * 0.2, 3),
                        'common_interests': []
                    },
                    'member_count': circle.member_count,
                    'match_reason': f"おすすめのサークルです（適合度: {int(base_score * 100)}%）"
                }
                circle_matches.append(match_data)
            
            return Response(circle_matches)
            
        except Exception as e:
            print(f"❌ フォールバックマッチングエラー: {e}")
            # 最終フォールバック: 空のリスト
            return Response([])
    
    @action(detail=False, methods=['get'])
    def recommendations(self, request):
        """おすすめユーザー・サークルを取得"""
        recommendation_type = request.query_params.get('type', 'users')
        
        if recommendation_type == 'circles':
            return self.find_circle_matches(request)
        else:
            return self.find_user_matches(request)
    
    @action(detail=False, methods=['get'])
    def recommended_circles(self, request):
        """おすすめサークルを取得（専用エンドポイント）"""
        current_user = self.request.user
        limit = int(request.query_params.get('limit', 10))
        algorithm = request.query_params.get('algorithm', 'smart')
        
        print(f"\n🎯 =============== おすすめサークル取得開始 ===============")
        print(f"👤 リクエストユーザー: {current_user}")
        print(f"🔧 アルゴリズム: {algorithm}")
        print(f"📊 取得制限数: {limit}")
        
        # ログレベルを一時的にDEBUGに設定
        import logging
        recommendation_logger = logging.getLogger('knest_backend.apps.recommendations.engines')
        original_level = recommendation_logger.level
        recommendation_logger.setLevel(logging.DEBUG)
        
        try:
            # 次世代推薦エンジンでおすすめサークルを取得
            from ..recommendations.engines import NextGenRecommendationEngine
            engine = NextGenRecommendationEngine(current_user)
            
            recommendations = engine.generate_recommendations(
                algorithm=algorithm,
                limit=limit,
                diversity_factor=0.5  # 多様性を重視
            )
            
            print(f"\n💾 推薦エンジンが返したサークル:")
            for i, rec in enumerate(recommendations['recommendations'], 1):
                circle = rec['circle']
                score_breakdown = rec.get('score_breakdown', {})
                
                print(f"   {i}. DB ID: {circle.id}")
                print(f"      Name: {circle.name}")
                print(f"      Total Score: {rec['score']:.3f}")
                print(f"      Confidence: {rec['confidence']:.3f}")
                
                # スコア内訳を詳細表示
                if score_breakdown:
                    total = score_breakdown.get('total', rec['score'])
                    print(f"      === スコア内訳 ===")
                    print(f"      階層マッチング: {score_breakdown.get('hierarchical', 0):.3f} ({score_breakdown.get('hierarchical', 0)/total*100:.1f}%)")
                    print(f"      協調フィルタリング: {score_breakdown.get('collaborative', 0):.3f} ({score_breakdown.get('collaborative', 0)/total*100:.1f}%)")
                    print(f"      行動ベース: {score_breakdown.get('behavioral', 0):.3f} ({score_breakdown.get('behavioral', 0)/total*100:.1f}%)")
                    print(f"      多様性保証: {score_breakdown.get('diversity', 0):.3f} ({score_breakdown.get('diversity', 0)/total*100:.1f}%)")
                    print(f"      人気度ボーナス: {score_breakdown.get('popularity', 0):.3f} ({score_breakdown.get('popularity', 0)/total*100:.1f}%)")
                    print(f"      ================")
                
                # 推薦理由の詳細表示
                reasons = rec.get('reasons', [])
                print(f"      推薦理由:")
                for j, reason in enumerate(reasons, 1):
                    weight = reason.get('weight', 0)
                    contribution_pct = reason.get('contribution_percentage', 0)
                    print(f"        {j}. {reason['type']}: {reason['detail']}")
                    print(f"           重み: {weight:.3f}, 寄与率: {contribution_pct:.1f}%")
            
            # レスポンス形式を整理
            response_data = {
                'circles': [],
                'algorithm_used': algorithm,
                'algorithm_weights': recommendations.get('algorithm_weights', {}),
                'computation_time_ms': recommendations.get('computation_time_ms', 0),
                'total_candidates': recommendations.get('total_candidates', 0)
            }
            
            # アルゴリズム重みも詳細ログ出力
            algorithm_weights = recommendations.get('algorithm_weights', {})
            print(f"\n📊 使用されたアルゴリズム重み:")
            for algorithm_name, weight in algorithm_weights.items():
                print(f"   {algorithm_name}: {weight:.3f}")
            
            print(f"\n📡 フロントエンドに送信するサークルデータ:")
            for i, rec in enumerate(recommendations['recommendations'], 1):
                circle = rec['circle']
                score = rec['score']
                reasons = rec['reasons']
                confidence = rec['confidence']
                score_breakdown = rec.get('score_breakdown', {})
                
                # UUIDを新規生成（マッチング用の一意ID）
                match_id = str(uuid.uuid4())
                print(f"   {i}. 送信データ:")
                print(f"      Match ID: {match_id}")
                print(f"      Circle ID: {circle.id}")
                print(f"      Circle Name: {circle.name}")
                print(f"      Score: {score:.3f}")
                
                # 詳細なマッチング情報を含むレスポンス
                circle_data = {
                    'id': match_id,
                    'circle': {
                        'id': str(circle.id),
                        'name': circle.name,
                        'description': circle.description,
                        'status': circle.status,
                        'circle_type': circle.circle_type,
                        'member_count': circle.member_count,
                        'post_count': circle.post_count,
                        'tags': circle.tags,
                        'icon_url': circle.icon_url,
                        'cover_url': circle.cover_url,
                        'created_at': circle.created_at.isoformat(),
                        'updated_at': circle.updated_at.isoformat(),
                        'last_activity_at': circle.last_activity.isoformat(),
                        'owner': {
                            'id': str(circle.owner.id),
                            'username': circle.owner.username,
                            'display_name': getattr(circle.owner, 'display_name', circle.owner.username)
                        }
                    },
                    'matching_details': {
                        'total_score': round(score, 3),
                        'confidence': round(confidence, 3),
                        'score_breakdown': score_breakdown,
                        'reasons': [{
                            'type': reason['type'],
                            'detail': reason['detail'],
                            'weight': reason['weight'],
                            'explanation': reason.get('explanation', ''),
                            'contribution_percentage': reason.get('contribution_percentage', 0)
                        } for reason in reasons],
                        'match_explanation': self._generate_detailed_explanation(reasons, score)
                    },
                    'member_count': circle.member_count,
                    'match_reason': self._format_match_reason(reasons, score)
                }
                response_data['circles'].append(circle_data)
            
            print(f"✅ 推薦サークル送信完了 ({len(response_data['circles'])}件)")
            print(f"===============================================================\n")
            
            # ログレベルを元に戻す
            recommendation_logger.setLevel(original_level)
            
            return Response(response_data)
            
        except Exception as e:
            print(f"❌ おすすめサークル取得エラー: {e}")
            print(f"🔄 フォールバック処理に移行します")
            
            # ログレベルを元に戻す
            recommendation_logger.setLevel(original_level)
            
            # フォールバック処理
            return self._fallback_recommended_circles(current_user, limit)
    
    def _generate_detailed_explanation(self, reasons, score):
        """詳細なマッチング説明を生成"""
        if not reasons:
            return "基本的な推薦アルゴリズムに基づいています"
        
        explanations = []
        for reason in reasons:
            if reason['type'] == 'interest_match':
                explanations.append(f"共通の興味関心: {reason['detail']}")
            elif reason['type'] == 'similar_users':
                explanations.append(f"類似ユーザーの参加: {reason['detail']}")
            elif reason['type'] == 'activity_pattern':
                explanations.append(f"行動パターン一致: {reason['detail']}")
        
        return "; ".join(explanations)
    
    def _fallback_recommended_circles(self, user, limit):
        """フォールバック用おすすめサークル"""
        from ..circles.recommendation import get_personalized_recommendations
        
        try:
            circles = get_personalized_recommendations(user, algorithm='weighted', limit=limit)
            
            response_data = {
                'circles': [],
                'algorithm_used': 'fallback_weighted',
                'computation_time_ms': 0,
                'total_candidates': len(circles)
            }
            
            for i, circle in enumerate(circles):
                base_score = max(0.4, 0.9 - (i * 0.05))
                
                circle_data = {
                    'id': str(uuid.uuid4()),
                    'circle': {
                        'id': str(circle.id),
                        'name': circle.name,
                        'description': circle.description,
                        'status': circle.status,
                        'circle_type': circle.circle_type,
                        'member_count': circle.member_count,
                        'post_count': circle.post_count,
                        'tags': circle.tags,
                        'icon_url': circle.icon_url,
                        'cover_url': circle.cover_url,
                        'created_at': circle.created_at.isoformat(),
                        'updated_at': circle.updated_at.isoformat(),
                        'last_activity_at': circle.last_activity.isoformat(),
                        'owner': {
                            'id': str(circle.owner.id),
                            'username': circle.owner.username,
                            'display_name': getattr(circle.owner, 'display_name', circle.owner.username)
                        }
                    },
                    'matching_details': {
                        'total_score': round(base_score, 3),
                        'confidence': round(base_score * 0.8, 3),
                        'reasons': [{'type': 'popularity', 'detail': '人気のサークル', 'weight': 1.0}],
                        'match_explanation': '人気度と基本的な適合性に基づく推薦'
                    },
                    'member_count': circle.member_count,
                    'match_reason': f"人気のサークルです（適合度: {int(base_score * 100)}%）"
                }
                response_data['circles'].append(circle_data)
            
            return Response(response_data)
            
        except Exception as e:
            print(f"❌ フォールバック推薦エラー: {e}")
            return Response({
                'circles': [],
                'algorithm_used': 'error',
                'computation_time_ms': 0,
                'total_candidates': 0
            }) 