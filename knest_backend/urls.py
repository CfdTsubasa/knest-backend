"""knest_backend URL Configuration"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Knest API",
        default_version='v1',
        description="KnestアプリケーションのバックエンドAPI",
        terms_of_service="https://www.knest.app/terms/",
        contact=openapi.Contact(email="contact@knest.app"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('knest_backend.apps.users.urls')),
    path('api/interests/', include('knest_backend.apps.interests.urls')),
    path('api/circles/', include('knest_backend.apps.circles.urls')),
    path('api/ai-support/', include('knest_backend.apps.ai_support.urls')),
    path('api/subscriptions/', include('knest_backend.apps.subscriptions.urls')),
    # Swagger URLs
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
] 