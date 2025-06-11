from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, CircleViewSet, CirclePostViewSet,
    CircleEventViewSet, CircleChatViewSet
)

router = DefaultRouter()
router.register('categories', CategoryViewSet)
router.register('circles', CircleViewSet, basename='circle')
router.register('posts', CirclePostViewSet, basename='circle-post')
router.register('events', CircleEventViewSet, basename='circle-event')
router.register('chats', CircleChatViewSet, basename='circle-chat')

urlpatterns = [
    path('', include(router.urls)),
] 