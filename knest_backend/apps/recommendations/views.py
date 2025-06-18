from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db import transaction
import uuid

from ..circles.models import Circle
from ..circles.serializers import CircleSerializer
from .models import UserRecommendationFeedback, RecommendationMetrics
from .engines import NextGenRecommendationEngine
from .serializers import UserRecommendationFeedbackSerializer


class RecommendationViewSet(viewsets.ViewSet):
    """次世代推薦システムのAPIビューセット"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def circles(self, request):
        """
        サークル推薦エンドポイント
        
        Query Parameters:
        - algorithm: 'smart' | 'content' | 'collaborative' | 'behavioral' (default: 'smart')
        - limit: int (default: 10)
        - diversity_factor: float (0.0-1.0, default: 0.3)
        - exclude_categories: list[str]
        - include_new_circles: boolean
        """
        # パラメータ取得
        algorithm = request.query_params.get('algorithm', 'smart')
        limit = int(request.query_params.get('limit', 10))
        diversity_factor = float(request.query_params.get('diversity_factor', 0.3))
        exclude_categories = request.query_params.getlist('exclude_categories', [])
        include_new_circles = request.query_params.get('include_new_circles', 'true').lower() == 'true'
        
        # パラメータバリデーション
        if algorithm not in ['smart', 'content', 'collaborative', 'behavioral']:
            return Response(
                {'error': 'Invalid algorithm. Choose from: smart, content, collaborative, behavioral'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not (1 <= limit <= 50):
            return Response(
                {'error': 'Limit must be between 1 and 50'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # 推薦エンジン初期化
            engine = NextGenRecommendationEngine(request.user)
            
            # 推薦生成
            recommendation_result = engine.generate_recommendations(
                algorithm=algorithm,
                limit=limit,
                diversity_factor=diversity_factor
            )
            
            # セッションID生成（フィードバック追跡用）
            session_id = str(uuid.uuid4())
            
            # 推薦結果をシリアライズ
            serialized_recommendations = []
            for item in recommendation_result['recommendations']:
                circle_data = CircleSerializer(item['circle']).data
                serialized_recommendations.append({
                    'circle': circle_data,
                    'score': round(item['score'], 3),
                    'reasons': item['reasons'],
                    'confidence': round(item['confidence'], 3),
                    'session_id': session_id
                })
            
            # レスポンス構築
            response_data = {
                'recommendations': serialized_recommendations,
                'algorithm_used': algorithm,
                'algorithm_weights': {
                    k: round(v, 3) for k, v in recommendation_result['algorithm_weights'].items()
                },
                'count': len(serialized_recommendations),
                'total_candidates': recommendation_result['total_candidates'],
                'computation_time_ms': round(recommendation_result['computation_time_ms'], 1),
                'session_id': session_id,
                'generated_at': timezone.now().isoformat()
            }
            
            return Response(response_data)
            
        except Exception as e:
            return Response(
                {'error': f'推薦生成中にエラーが発生しました: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def feedback(self, request):
        """
        推薦結果に対するフィードバックを記録
        
        POST Data:
        - circle_id: UUID
        - feedback_type: 'view' | 'click' | 'join_request' | 'join_success' | 'dismiss' | 'not_interested' | 'bookmark' | 'share'
        - session_id: string
        - recommendation_score: float (optional)
        - recommendation_algorithm: string (optional)
        - recommendation_reasons: list (optional)
        """
        try:
            circle_id = request.data.get('circle_id')
            feedback_type = request.data.get('feedback_type')
            session_id = request.data.get('session_id')
            
            # 必須パラメータチェック
            if not all([circle_id, feedback_type]):
                return Response(
                    {'error': 'circle_id and feedback_type are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # フィードバックタイプバリデーション
            valid_feedback_types = [
                'view', 'click', 'join_request', 'join_success', 
                'dismiss', 'not_interested', 'bookmark', 'share'
            ]
            if feedback_type not in valid_feedback_types:
                return Response(
                    {'error': f'Invalid feedback_type. Choose from: {", ".join(valid_feedback_types)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # サークル存在確認
            try:
                circle = Circle.objects.get(id=circle_id)
            except Circle.DoesNotExist:
                return Response(
                    {'error': 'Circle not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # フィードバック記録
            with transaction.atomic():
                feedback = UserRecommendationFeedback.objects.create(
                    user=request.user,
                    circle=circle,
                    feedback_type=feedback_type,
                    recommendation_score=request.data.get('recommendation_score', 0.0),
                    recommendation_algorithm=request.data.get('recommendation_algorithm', 'unknown'),
                    recommendation_reasons=request.data.get('recommendation_reasons', []),
                    session_id=session_id
                )
            
            # フィードバック統計更新（非同期で実行可能）
            self._update_feedback_metrics(feedback)
            
            serializer = UserRecommendationFeedbackSerializer(feedback)
            return Response({
                'message': 'フィードバックが正常に記録されました',
                'feedback': serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': f'フィードバック記録中にエラーが発生しました: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def metrics(self, request):
        """
        推薦システムのメトリクス取得
        
        Query Parameters:
        - algorithm: string (optional)
        - start_date: YYYY-MM-DD (optional)
        - end_date: YYYY-MM-DD (optional)
        - metric_type: string (optional)
        """
        try:
            # パラメータ取得
            algorithm = request.query_params.get('algorithm')
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            metric_type = request.query_params.get('metric_type')
            
            # メトリクス取得
            metrics_queryset = RecommendationMetrics.objects.all()
            
            if algorithm:
                metrics_queryset = metrics_queryset.filter(algorithm_name=algorithm)
            if start_date:
                metrics_queryset = metrics_queryset.filter(measurement_date__gte=start_date)
            if end_date:
                metrics_queryset = metrics_queryset.filter(measurement_date__lte=end_date)
            if metric_type:
                metrics_queryset = metrics_queryset.filter(metric_type=metric_type)
            
            metrics_queryset = metrics_queryset.order_by('-measurement_date')[:100]
            
            # レスポンス構築
            metrics_data = []
            for metric in metrics_queryset:
                metrics_data.append({
                    'id': metric.id,
                    'metric_type': metric.metric_type,
                    'algorithm_name': metric.algorithm_name,
                    'metric_value': metric.metric_value,
                    'user_segment': metric.user_segment,
                    'measurement_date': metric.measurement_date.isoformat(),
                    'created_at': metric.created_at.isoformat()
                })
            
            return Response({
                'metrics': metrics_data,
                'count': len(metrics_data)
            })
            
        except Exception as e:
            return Response(
                {'error': f'メトリクス取得中にエラーが発生しました: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def user_preferences(self, request):
        """
        ユーザーの推薦設定と学習された好みを取得
        """
        try:
            engine = NextGenRecommendationEngine(request.user)
            
            # ユーザープロファイル分析
            user_profile = engine._analyze_user_profile()
            
            # 学習された好みパターン
            learning_patterns = engine.learning_engine.get_user_feedback_patterns()
            
            # アルゴリズム重み
            algorithm_weights = engine.calculate_algorithm_weights()
            
            response_data = {
                'user_profile': user_profile,
                'algorithm_weights': {
                    k: round(v, 3) for k, v in algorithm_weights.items()
                },
                'learning_patterns': {
                    'preferred_categories': dict(learning_patterns['preferred_categories']),
                    'disliked_categories': dict(learning_patterns['disliked_categories']),
                    'successful_algorithms': dict(learning_patterns['successful_algorithms'])
                },
                'recommendations_received_count': UserRecommendationFeedback.objects.filter(
                    user=request.user
                ).count(),
                'generated_at': timezone.now().isoformat()
            }
            
            return Response(response_data)
            
        except Exception as e:
            return Response(
                {'error': f'ユーザー設定取得中にエラーが発生しました: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _update_feedback_metrics(self, feedback):
        """フィードバックに基づいてメトリクスを更新"""
        try:
            # CTR計算など、メトリクス更新ロジック
            # 実際の実装では非同期タスク（Celery）で実行することを推奨
            pass
        except Exception as e:
            # メトリクス更新エラーは推薦システムの動作を止めない
            print(f"メトリクス更新エラー: {e}")
            pass 