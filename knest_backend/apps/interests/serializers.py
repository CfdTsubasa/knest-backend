from rest_framework import serializers
from .models import (
    Interest, UserInterest,
    InterestCategory, InterestSubcategory, InterestTag, UserInterestProfile
)

class InterestSerializer(serializers.ModelSerializer):
    """興味のシリアライザー"""
    class Meta:
        model = Interest
        fields = ['id', 'name', 'description', 'category', 'is_official', 'usage_count', 'icon_url', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class UserInterestSerializer(serializers.ModelSerializer):
    """ユーザー興味関心シリアライザー（シンプル版）"""
    interest = InterestSerializer(read_only=True)
    interest_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = UserInterest
        fields = ['id', 'interest', 'interest_id', 'added_at']
        read_only_fields = ['id', 'added_at']
    
    def validate_interest_id(self, value):
        """interest_idのバリデーション"""
        try:
            Interest.objects.get(id=value)
            return value
        except Interest.DoesNotExist:
            raise serializers.ValidationError("指定された興味が見つかりません。") 

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
    category_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = InterestSubcategory
        fields = ['id', 'category', 'category_id', 'name', 'description', 'created_at']


class InterestTagSerializer(serializers.ModelSerializer):
    """興味関心タグシリアライザー"""
    subcategory = InterestSubcategorySerializer(read_only=True)
    subcategory_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = InterestTag
        fields = ['id', 'subcategory', 'subcategory_id', 'name', 'description', 'usage_count', 'created_at']


class UserInterestProfileSerializer(serializers.ModelSerializer):
    """ユーザー興味関心プロフィールシリアライザー"""
    category = InterestCategorySerializer(read_only=True)
    subcategory = InterestSubcategorySerializer(read_only=True)
    tag = InterestTagSerializer(read_only=True)
    tag_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = UserInterestProfile
        fields = ['id', 'user', 'category', 'subcategory', 'tag', 'tag_id', 'added_at']
        read_only_fields = ['id', 'user', 'category', 'subcategory', 'added_at']

    def create(self, validated_data):
        # ユーザーは現在認証されているユーザーを設定
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class HierarchicalInterestTreeSerializer(serializers.ModelSerializer):
    """階層構造を含む完全なツリー表示用シリアライザー"""
    subcategories = serializers.SerializerMethodField()
    
    class Meta:
        model = InterestCategory
        fields = ['id', 'name', 'type', 'description', 'icon_url', 'subcategories']
    
    def get_subcategories(self, obj):
        subcategories = obj.subcategories.all()
        return [{
            'id': sub.id,
            'name': sub.name,
            'description': sub.description,
            'tags': [{
                'id': tag.id,
                'name': tag.name,
                'description': tag.description,
                'usage_count': tag.usage_count
            } for tag in sub.interest_tags.all()]
        } for sub in subcategories]


# マッチング関連シリアライザー
class MatchingScoreSerializer(serializers.Serializer):
    """マッチングスコアシリアライザー"""
    total_score = serializers.FloatField()
    interest_score = serializers.FloatField()
    location_score = serializers.FloatField()
    age_score = serializers.FloatField()
    common_interests = serializers.ListField(child=serializers.CharField())


class UserMatchSerializer(serializers.Serializer):
    """ユーザーマッチング結果シリアライザー"""
    from django.contrib.auth import get_user_model
    from ..users.serializers import UserSerializer
    
    id = serializers.UUIDField()
    user = UserSerializer()
    score = MatchingScoreSerializer()
    match_reason = serializers.CharField()


class CircleMatchSerializer(serializers.Serializer):
    """サークルマッチング結果シリアライザー"""
    # TODO: サークルシリアライザーが実装されたら追加
    # from ..circles.serializers import CircleSerializer
    
    id = serializers.UUIDField()
    # circle = CircleSerializer()
    score = MatchingScoreSerializer()
    member_count = serializers.IntegerField()
    match_reason = serializers.CharField() 