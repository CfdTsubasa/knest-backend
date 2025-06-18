from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RecommendationViewSet

app_name = 'recommendations'

router = DefaultRouter()
router.register(r'', RecommendationViewSet, basename='recommendation')

urlpatterns = [
    path('', include(router.urls)),
] 