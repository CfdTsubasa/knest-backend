from rest_framework import serializers
from .models import (
    UserRecommendationFeedback,
    UserSimilarity,
    RecommendationExperiment,
    RecommendationMetrics,
    UserInteractionHistory
)


class UserRecommendationFeedbackSerializer(serializers.ModelSerializer):
    """ユーザー推薦フィードバックシリアライザー"""
    
    class Meta:
        model = UserRecommendationFeedback
        fields = [
            'id', 'user', 'circle', 'feedback_type',
            'recommendation_score', 'recommendation_algorithm',
            'recommendation_reasons', 'session_id', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class UserSimilaritySerializer(serializers.ModelSerializer):
    """ユーザー類似度シリアライザー"""
    
    class Meta:
        model = UserSimilarity
        fields = [
            'id', 'user1', 'user2', 'similarity_score',
            'calculation_method', 'calculated_at'
        ]
        read_only_fields = ['id', 'calculated_at']


class RecommendationExperimentSerializer(serializers.ModelSerializer):
    """推薦実験シリアライザー"""
    
    class Meta:
        model = RecommendationExperiment
        fields = [
            'id', 'name', 'description', 'algorithm_config',
            'target_user_ratio', 'status', 'start_date', 'end_date',
            'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class RecommendationMetricsSerializer(serializers.ModelSerializer):
    """推薦メトリクスシリアライザー"""
    
    class Meta:
        model = RecommendationMetrics
        fields = [
            'id', 'metric_type', 'algorithm_name', 'metric_value',
            'user_segment', 'experiment', 'measurement_date', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class UserInteractionHistorySerializer(serializers.ModelSerializer):
    """ユーザーインタラクション履歴シリアライザー"""
    
    class Meta:
        model = UserInteractionHistory
        fields = [
            'id', 'user', 'circle', 'action_type',
            'duration_seconds', 'context_data', 'created_at'
        ]
        read_only_fields = ['id', 'created_at'] 