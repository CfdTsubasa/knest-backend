from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    InterestCategoryViewSet,
    InterestSubcategoryViewSet,
    InterestTagViewSet,
    UserInterestProfileViewSet
)

router = DefaultRouter()
router.register(r'hierarchical/categories', InterestCategoryViewSet)
router.register(r'hierarchical/subcategories', InterestSubcategoryViewSet)
router.register(r'hierarchical/tags', InterestTagViewSet)
router.register(r'hierarchical/user-profiles', UserInterestProfileViewSet, basename='userinterestprofile')

urlpatterns = [
    path('', include(router.urls)),
] 