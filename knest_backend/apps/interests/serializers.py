from rest_framework import serializers
from .models import (
    InterestCategory, InterestSubcategory, InterestTag, UserInterestProfile
)

# ======================================
# 新しい3階層興味関心システム用シリアライザー
# ======================================

class InterestCategorySerializer(serializers.ModelSerializer):
    """興味関心カテゴリシリアライザー"""
    class Meta:
        model = InterestCategory
        fields = ['id', 'name', 'type', 'description', 'icon_url', 'created_at']

class InterestSubcategorySerializer(serializers.ModelSerializer):
    """興味関心サブカテゴリシリアライザー"""
    category = InterestCategorySerializer(read_only=True)
    
    class Meta:
        model = InterestSubcategory
        fields = ['id', 'category', 'name', 'description', 'created_at']

class InterestTagSerializer(serializers.ModelSerializer):
    """興味関心タグシリアライザー"""
    subcategory = InterestSubcategorySerializer(read_only=True)
    
    class Meta:
        model = InterestTag
        fields = ['id', 'subcategory', 'name', 'description', 'usage_count', 'created_at']

class UserInterestProfileSerializer(serializers.ModelSerializer):
    """ユーザー興味関心プロフィールシリアライザー"""
    category = InterestCategorySerializer(read_only=True)
    subcategory = InterestSubcategorySerializer(read_only=True)
    tag = InterestTagSerializer(read_only=True)
    
    class Meta:
        model = UserInterestProfile
        fields = ['id', 'user', 'category', 'subcategory', 'tag', 'level', 'added_at']
        read_only_fields = ['id', 'user', 'added_at']

class HierarchicalInterestTreeSerializer(serializers.Serializer):
    """階層型興味関心ツリーシリアライザー"""
    categories = InterestCategorySerializer(many=True)
    subcategories = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    
    def get_subcategories(self, obj):
        subcategories = {}
        for category in obj['categories']:
            subcategories[category.id] = InterestSubcategorySerializer(
                InterestSubcategory.objects.filter(category=category),
                many=True
            ).data
        return subcategories
    
    def get_tags(self, obj):
        tags = {}
        for category in obj['categories']:
            category_tags = {}
            subcategories = InterestSubcategory.objects.filter(category=category)
            for subcategory in subcategories:
                category_tags[subcategory.id] = InterestTagSerializer(
                    InterestTag.objects.filter(subcategory=subcategory),
                    many=True
                ).data
            tags[category.id] = category_tags
        return tags

# リクエストシリアライザー
class CreateUserInterestProfileCategoryRequestSerializer(serializers.Serializer):
    """カテゴリレベルでの興味追加リクエスト"""
    category_id = serializers.UUIDField()
    level = serializers.IntegerField(default=1)

class CreateUserInterestProfileSubcategoryRequestSerializer(serializers.Serializer):
    """サブカテゴリレベルでの興味追加リクエスト"""
    category_id = serializers.UUIDField()
    subcategory_id = serializers.UUIDField()
    level = serializers.IntegerField(default=2) 