from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    InterestViewSet, UserInterestViewSet, TagViewSet, UserTagViewSet,
    InterestCategoryViewSet, InterestSubcategoryViewSet, InterestTagViewSet,
    UserInterestProfileViewSet, HierarchicalInterestTreeViewSet, MatchingEngineViewSet
)

# DRF Router設定
router = DefaultRouter()
router.register(r'interests', InterestViewSet)
router.register(r'user-interests', UserInterestViewSet, basename='user-interests')
router.register(r'tags', TagViewSet)
router.register(r'user-tags', UserTagViewSet, basename='user-tags')

# 新しい3階層システム
router.register(r'hierarchical/categories', InterestCategoryViewSet)
router.register(r'hierarchical/subcategories', InterestSubcategoryViewSet)
router.register(r'hierarchical/tags', InterestTagViewSet)
router.register(r'hierarchical/user-profiles', UserInterestProfileViewSet, basename='userinterestprofile')
router.register(r'hierarchical/tree', HierarchicalInterestTreeViewSet)

# マッチングエンジン
router.register(r'matching', MatchingEngineViewSet, basename='matching')

app_name = 'interests'

urlpatterns = [
    # API endpoints - 直接router.urlsをinclude
    path('', include(router.urls)),
] 