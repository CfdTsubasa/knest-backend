"""
サークル推薦システム
"""
from django.db import models
from django.db.models import Count, Q, Avg, F
from .models import Circle
from ..interests.models import UserInterest
from ..users.models import User
import math
from collections import defaultdict


class CircleRecommendationEngine:
    """サークル推薦エンジン"""
    
    def __init__(self, user):
        self.user = user
        self.user_interests = UserInterest.objects.filter(user=user)
    
    def get_recommendations(self, algorithm='hybrid', limit=10):
        """推薦サークルを取得"""
        if algorithm == 'simple':
            return self._simple_matching(limit)
        elif algorithm == 'weighted':
            return self._weighted_scoring(limit)
        elif algorithm == 'collaborative':
            return self._collaborative_filtering(limit)
        elif algorithm == 'hybrid':
            return self._hybrid_approach(limit)
        else:
            return self._simple_matching(limit)
    
    def _simple_matching(self, limit):
        """シンプルな興味関心マッチング"""
        if not self.user_interests.exists():
            # 興味関心がない場合は人気サークルを返す
            return Circle.objects.filter(
                status='open'
            ).order_by('-member_count')[:limit]
        
        user_interest_ids = self.user_interests.values_list('interest_id', flat=True)
        
        circles = Circle.objects.filter(
            status='open',
            interests__in=user_interest_ids
        ).annotate(
            match_count=Count('interests', filter=Q(interests__in=user_interest_ids)),
            distinct_matches=Count('interests', distinct=True, filter=Q(interests__in=user_interest_ids))
        ).exclude(
            # 既に参加済みのサークルを除外
            memberships__user=self.user,
            memberships__status='active'
        ).order_by('-distinct_matches', '-member_count')[:limit]
        
        return circles
    
    def _weighted_scoring(self, limit):
        """重み付けスコアリング（シンプル版）"""
        circles_scores = []
        user_interest_ids = set(self.user_interests.values_list('interest_id', flat=True))
        
        circles = Circle.objects.filter(status='open').exclude(
            memberships__user=self.user,
            memberships__status='active'
        ).prefetch_related('interests')
        
        for circle in circles:
            score = self._calculate_circle_score(circle, user_interest_ids)
            if score > 0:
                circles_scores.append((circle, score))
        
        # スコア順でソート
        circles_scores.sort(key=lambda x: x[1], reverse=True)
        return [circle for circle, score in circles_scores[:limit]]
    
    def _calculate_circle_score(self, circle, user_interest_ids):
        """サークルのスコアを計算（シンプル版）"""
        score = 0
        
        # 1. 興味関心マッチングスコア（シンプル）
        matching_interests = 0
        for interest in circle.interests.all():
            if interest.id in user_interest_ids:
                matching_interests += 1
                score += 30  # 基本マッチスコア
        
        # 2. マッチング度ボーナス（複数マッチでボーナス）
        if matching_interests >= 3:
            score += 50  # 3つ以上マッチで大ボーナス
        elif matching_interests >= 2:
            score += 20  # 2つマッチで小ボーナス
        
        # 3. サークルの活発さスコア
        activity_score = min(circle.member_count * 0.5, 40)  # 最大40点
        post_activity = min(circle.post_count * 0.1, 20)     # 最大20点
        score += activity_score + post_activity
        
        # 4. サークルの新鮮さスコア（新しいサークルを少し優遇）
        import datetime
        days_since_creation = (datetime.datetime.now().date() - circle.created_at.date()).days
        if days_since_creation < 30:
            score += 15  # 新規サークルボーナス
        elif days_since_creation < 90:
            score += 8   # 比較的新しいサークル
        
        # 5. 満員度ペナルティ
        if circle.member_limit and circle.member_count >= circle.member_limit * 0.9:
            score *= 0.6  # 90%以上埋まっている場合はスコア40%減
        elif circle.member_limit and circle.member_count >= circle.member_limit * 0.7:
            score *= 0.8  # 70%以上埋まっている場合はスコア20%減
        
        return score
    
    def _collaborative_filtering(self, limit):
        """協調フィルタリング（類似ユーザーベース）"""
        # 類似ユーザーを見つける
        similar_users = self._find_similar_users()
        
        # 類似ユーザーが参加しているサークルを推薦
        recommended_circles = Circle.objects.filter(
            memberships__user__in=similar_users,
            memberships__status='active',
            status='open'
        ).exclude(
            memberships__user=self.user,
            memberships__status='active'
        ).annotate(
            similar_user_count=Count('memberships__user', filter=Q(
                memberships__user__in=similar_users,
                memberships__status='active'
            ))
        ).order_by('-similar_user_count', '-member_count')[:limit]
        
        return recommended_circles
    
    def _find_similar_users(self, limit=20):
        """類似ユーザーを見つける"""
        if not self.user_interests.exists():
            return User.objects.none()
        
        user_interest_ids = set(self.user_interests.values_list('interest_id', flat=True))
        
        # 共通の興味関心を持つユーザーを検索
        similar_users = User.objects.filter(
            userinterest__interest_id__in=user_interest_ids
        ).exclude(
            id=self.user.id
        ).annotate(
            common_interests=Count('userinterest__interest', filter=Q(
                userinterest__interest_id__in=user_interest_ids
            ))
        ).filter(
            common_interests__gte=2  # 最低2つの共通興味関心
        ).order_by('-common_interests')[:limit]
        
        return similar_users
    
    def _hybrid_approach(self, limit):
        """ハイブリッドアプローチ"""
        # 各アルゴリズムの結果を組み合わせ
        simple_results = list(self._simple_matching(limit))
        weighted_results = list(self._weighted_scoring(limit))
        collab_results = list(self._collaborative_filtering(limit // 2))
        
        # 重複を除去しつつ結合
        seen_ids = set()
        final_results = []
        
        # 重み付けスコアリングの結果を優先
        for circle in weighted_results:
            if circle.id not in seen_ids:
                final_results.append(circle)
                seen_ids.add(circle.id)
        
        # 協調フィルタリングの結果を追加
        for circle in collab_results:
            if circle.id not in seen_ids and len(final_results) < limit:
                final_results.append(circle)
                seen_ids.add(circle.id)
        
        # シンプルマッチングで残りを埋める
        for circle in simple_results:
            if circle.id not in seen_ids and len(final_results) < limit:
                final_results.append(circle)
                seen_ids.add(circle.id)
        
        return final_results[:limit]


def get_personalized_recommendations(user, algorithm='hybrid', limit=10):
    """ユーザー向けのパーソナライズド推薦を取得"""
    engine = CircleRecommendationEngine(user)
    return engine.get_recommendations(algorithm=algorithm, limit=limit)


def get_trending_circles(limit=10):
    """トレンドサークルを取得"""
    from datetime import datetime, timedelta
    
    # 過去7日間の活動を基にトレンドを計算
    week_ago = datetime.now() - timedelta(days=7)
    
    trending = Circle.objects.filter(
        status='open'
    ).annotate(
        recent_activity=Count('posts', filter=Q(posts__created_at__gte=week_ago))
    ).order_by('-recent_activity', '-member_count')[:limit]
    
    return trending 