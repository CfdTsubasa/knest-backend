"""
推薦システム v1 → v2 移行ブリッジ
既存システムと新システムを段階的に統合
"""
from django.conf import settings
from ..recommendations.engines import NextGenRecommendationEngine
from .recommendation import CircleRecommendationEngine


def get_circle_recommendations_v2(user, algorithm='smart', limit=10, use_new_engine=True):
    """
    推薦システム v2 エントリーポイント
    設定により新旧エンジンを切り替え可能
    """
    if use_new_engine and getattr(settings, 'USE_NEW_RECOMMENDATION_ENGINE', False):
        # 新エンジンを使用
        try:
            engine = NextGenRecommendationEngine(user)
            result = engine.generate_recommendations(
                algorithm=algorithm,
                limit=limit
            )
            
            # 旧形式に変換
            circles = [item['circle'] for item in result['recommendations']]
            return circles
            
        except Exception as e:
            # エラー時は旧エンジンにフォールバック
            print(f"新推薦エンジンエラー、旧エンジンにフォールバック: {e}")
            return _fallback_to_old_engine(user, algorithm, limit)
    else:
        # 旧エンジンを使用
        return _fallback_to_old_engine(user, algorithm, limit)


def _fallback_to_old_engine(user, algorithm, limit):
    """旧推薦エンジンへのフォールバック"""
    old_engine = CircleRecommendationEngine(user)
    return old_engine.get_recommendations(algorithm=algorithm, limit=limit)


def track_user_interaction(user, circle, action_type, duration_seconds=None, context_data=None):
    """
    ユーザーインタラクションをトラッキング
    新推薦システムの学習機能をサポート
    """
    if not getattr(settings, 'USE_NEW_RECOMMENDATION_ENGINE', False):
        return
    
    try:
        from ..recommendations.models import UserInteractionHistory
        
        UserInteractionHistory.objects.create(
            user=user,
            circle=circle,
            action_type=action_type,
            duration_seconds=duration_seconds,
            context_data=context_data or {}
        )
    except Exception as e:
        # インタラクショントラッキングエラーは無視
        print(f"インタラクショントラッキングエラー: {e}")
        pass 