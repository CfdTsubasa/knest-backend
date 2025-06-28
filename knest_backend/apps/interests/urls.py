from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    InterestViewSet, UserInterestViewSet,
    InterestCategoryViewSet, InterestSubcategoryViewSet, InterestTagViewSet, UserInterestProfileViewSet,
    HierarchicalInterestTreeViewSet, MatchingEngineViewSet
)

# DRF Router設定
router = DefaultRouter()
router.register(r'interests', InterestViewSet, basename='interest')
router.register(r'user-interests', UserInterestViewSet, basename='user-interest')
router.register(r'categories', InterestCategoryViewSet, basename='category')
router.register(r'subcategories', InterestSubcategoryViewSet, basename='subcategory')
router.register(r'tags', InterestTagViewSet, basename='tag')
router.register(r'user-profiles', UserInterestProfileViewSet, basename='user-profile')
router.register(r'hierarchical-tree', HierarchicalInterestTreeViewSet, basename='hierarchical-tree')
router.register(r'matching', MatchingEngineViewSet, basename='matching')

app_name = 'interests'

urlpatterns = [
    # API endpoints - 直接router.urlsをinclude
    path('', include(router.urls)),
] 