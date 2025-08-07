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
    InterestCategory, InterestSubcategory, InterestTag, UserInterestProfile
)
from .serializers import (
    InterestCategorySerializer, InterestSubcategorySerializer, InterestTagSerializer,
    UserInterestProfileSerializer, HierarchicalInterestTreeSerializer,
    CreateUserInterestProfileCategoryRequestSerializer,
    CreateUserInterestProfileSubcategoryRequestSerializer
)
from ..users.models import User
from ..circles.models import Circle

User = get_user_model()

# ======================================
# 新しい3階層興味関心システム用ViewSet
# ======================================

class InterestCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """興味関心カテゴリViewSet"""
    queryset = InterestCategory.objects.all()
    serializer_class = InterestCategorySerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        # タイプでフィルタリング
        type_filter = self.request.query_params.get('type', None)
        if type_filter:
            queryset = queryset.filter(type=type_filter)
        
        # 検索クエリ
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        
        return queryset

class InterestSubcategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """興味関心サブカテゴリViewSet"""
    queryset = InterestSubcategory.objects.all()
    serializer_class = InterestSubcategorySerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        # カテゴリでフィルタリング
        category_id = self.request.query_params.get('category', None)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # 検索クエリ
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        
        return queryset

class InterestTagViewSet(viewsets.ReadOnlyModelViewSet):
    """興味関心タグViewSet"""
    queryset = InterestTag.objects.all()
    serializer_class = InterestTagSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        # サブカテゴリでフィルタリング
        subcategory_id = self.request.query_params.get('subcategory', None)
        if subcategory_id:
            queryset = queryset.filter(subcategory_id=subcategory_id)
        
        # 検索クエリ
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        
        return queryset.order_by('-usage_count', 'name')

    @action(detail=False, methods=['get'])
    def popular(self, request):
        """人気のタグを取得"""
        popular_tags = self.get_queryset().order_by('-usage_count')[:20]
        serializer = self.get_serializer(popular_tags, many=True)
        return Response(serializer.data)

class UserInterestProfileViewSet(viewsets.ModelViewSet):
    """ユーザー興味関心プロフィールViewSet"""
    serializer_class = UserInterestProfileSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return UserInterestProfile.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def add_category_level(self, request):
        """カテゴリレベルでの興味追加"""
        serializer = CreateUserInterestProfileCategoryRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        category_id = serializer.validated_data['category_id']
        level = serializer.validated_data.get('level', 1)
        
        try:
            category = InterestCategory.objects.get(id=category_id)
            profile = UserInterestProfile.objects.create(
                user=request.user,
                category=category,
                level=level
            )
            return Response(
                UserInterestProfileSerializer(profile).data,
                status=status.HTTP_201_CREATED
            )
        except InterestCategory.DoesNotExist:
            return Response(
                {'detail': '指定されたカテゴリが見つかりません。'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['post'])
    def add_subcategory_level(self, request):
        """サブカテゴリレベルでの興味追加"""
        serializer = CreateUserInterestProfileSubcategoryRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        category_id = serializer.validated_data['category_id']
        subcategory_id = serializer.validated_data['subcategory_id']
        level = serializer.validated_data.get('level', 2)
        
        try:
            category = InterestCategory.objects.get(id=category_id)
            subcategory = InterestSubcategory.objects.get(
                id=subcategory_id,
                category=category
            )
            profile = UserInterestProfile.objects.create(
                user=request.user,
                category=category,
                subcategory=subcategory,
                level=level
            )
            return Response(
                UserInterestProfileSerializer(profile).data,
                status=status.HTTP_201_CREATED
            )
        except (InterestCategory.DoesNotExist, InterestSubcategory.DoesNotExist):
            return Response(
                {'detail': '指定されたカテゴリまたはサブカテゴリが見つかりません。'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def tree(self, request):
        """階層型興味関心ツリーを取得"""
        categories = InterestCategory.objects.all()
        tree_data = {
            'categories': categories
        }
        serializer = HierarchicalInterestTreeSerializer(tree_data)
        return Response(serializer.data) 