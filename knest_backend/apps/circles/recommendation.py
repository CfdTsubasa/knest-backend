"""
サークル推薦システム
"""
from django.db import models
from django.db.models import Count, Q, Avg, F
from .models import Circle
from ..interests.models import UserInterestProfile, InterestTag
from ..users.models import User
import math
import random
from datetime import datetime, timedelta
from collections import defaultdict


class CircleRecommendationEngine:
    """サークル推薦エンジン"""
    
    def __init__(self, user):
        self.user = user
        self.user_interests = UserInterestProfile.objects.filter(user=user)
    
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
        """シンプルな興味関心マッチング（ランダム性追加）"""
        if not self.user_interests.exists():
            # 興味関心がない場合は人気サークル + ランダム要素
            circles = list(Circle.objects.filter(
                status='open'
            ).order_by('-member_count')[:limit * 2])  # 2倍取得
            
            # ランダムにシャッフルして限定数返す
            random.shuffle(circles)
            return circles[:limit]
        
        user_interest_ids = self.user_interests.values_list('tag_id', flat=True)
        
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
        ).order_by('-distinct_matches', '-member_count')
        
        # トップマッチをリスト化してランダマイズ
        circle_list = list(circles[:limit * 2])  # 2倍取得
        
        # スコアグループ化でランダマイズ
        score_groups = {}
        for circle in circle_list:
            score = circle.distinct_matches
            if score not in score_groups:
                score_groups[score] = []
            score_groups[score].append(circle)
        
        # 各スコアグループ内でランダマイズ
        final_result = []
        for score in sorted(score_groups.keys(), reverse=True):
            group = score_groups[score]
            random.shuffle(group)  # グループ内をシャッフル
            final_result.extend(group)
        
        return final_result[:limit]
    
    def _weighted_scoring(self, limit):
        """重み付けスコアリング（ランダム性とexploration追加）"""
        circles_scores = []
        user_interest_ids = set(self.user_interests.values_list('tag_id', flat=True))
        
        circles = Circle.objects.filter(status='open').exclude(
            memberships__user=self.user,
            memberships__status='active'
        ).prefetch_related('interests')
        
        for circle in circles:
            base_score = self._calculate_circle_score(circle, user_interest_ids)
            
            # ランダム探索要素（20%の確率で探索）
            exploration_bonus = 0
            if random.random() < 0.2:
                exploration_bonus = random.randint(10, 50)
            
            # 時間的多様性（アクセス時間に応じた微調整）
            time_variation = random.randint(-5, 15)
            
            final_score = base_score + exploration_bonus + time_variation
            
            if final_score > 0:
                circles_scores.append((circle, final_score))
        
        # スコア順でソート
        circles_scores.sort(key=lambda x: x[1], reverse=True)
        
        # トップ候補の中からランダムサンプリング
        top_candidates = circles_scores[:limit * 2]  # 2倍の候補取得
        
        # 80%確率で高スコア、20%確率でランダム選択
        final_selection = []
        used_indices = set()
        
        for i in range(min(limit, len(top_candidates))):
            if random.random() < 0.8 and i < len(top_candidates):
                # 高スコア優先選択
                if i not in used_indices:
                    final_selection.append(top_candidates[i][0])
                    used_indices.add(i)
            else:
                # ランダム選択
                available_indices = [j for j in range(len(top_candidates)) if j not in used_indices]
                if available_indices:
                    random_idx = random.choice(available_indices)
                    final_selection.append(top_candidates[random_idx][0])
                    used_indices.add(random_idx)
        
        return final_selection
    
    def _calculate_circle_score(self, circle, user_interest_ids):
        """サークルのスコアを計算（ランダム要素追加）"""
        score = 0
        
        # 1. 興味関心マッチングスコア
        matching_interests = 0
        for interest in circle.interests.all():
            if interest.id in user_interest_ids:
                matching_interests += 1
                score += 30  # 基本マッチスコア
        
        # 2. マッチング度ボーナス
        if matching_interests >= 3:
            score += 50
        elif matching_interests >= 2:
            score += 20
        
        # 3. サークルの活発さスコア
        activity_score = min(circle.member_count * 0.5, 40)
        post_activity = min(circle.post_count * 0.1, 20)
        score += activity_score + post_activity
        
        # 4. 新鮮さスコア（時間依存）
        days_since_creation = (datetime.now().date() - circle.created_at.date()).days
        if days_since_creation < 30:
            score += 15
        elif days_since_creation < 90:
            score += 8
        
        # 5. 満員度ペナルティ
        if circle.member_limit and circle.member_count >= circle.member_limit * 0.9:
            score *= 0.6
        elif circle.member_limit and circle.member_count >= circle.member_limit * 0.7:
            score *= 0.8
        
        # 6. 🎲 ランダム変動要素（±10%）
        randomness = random.uniform(0.9, 1.1)
        score *= randomness
        
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
        
        # ユーザーの興味関心タグを取得
        user_tags = set(self.user_interests.values_list('tag_id', flat=True))
        
        # 類似ユーザーを見つける
        similar_users = User.objects.filter(
            userinterestprofile__tag_id__in=user_tags
        ).exclude(
            id=self.user.id
        ).annotate(
            matching_tags=Count('userinterestprofile__tag', filter=Q(
                userinterestprofile__tag_id__in=user_tags
            ))
        ).filter(
            matching_tags__gt=0
        ).order_by('-matching_tags')[:limit]
        
        return similar_users

    def _hybrid_approach(self, limit):
        """ハイブリッドアプローチ（複数手法の組み合わせ）"""
        # 各手法の重み付け
        weights = {
            'simple': 0.3,
            'weighted': 0.4,
            'collaborative': 0.3
        }
        
        # 各手法で推薦を取得
        simple_recs = self._simple_matching(limit * 2)
        weighted_recs = self._weighted_scoring(limit * 2)
        collab_recs = self._collaborative_filtering(limit * 2)
        
        # スコアを集計
        circle_scores = defaultdict(float)
        
        for circle in simple_recs:
            circle_scores[circle] += weights['simple']
        
        for circle in weighted_recs:
            circle_scores[circle] += weights['weighted']
        
        for circle in collab_recs:
            circle_scores[circle] += weights['collaborative']
        
        # スコア順にソート
        sorted_circles = sorted(
            circle_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # 最終的な推薦リストを作成
        final_recommendations = []
        seen_circles = set()
        
        for circle, _ in sorted_circles:
            if circle.id not in seen_circles and len(final_recommendations) < limit:
                final_recommendations.append(circle)
                seen_circles.add(circle.id)
        
        return final_recommendations


def get_personalized_recommendations(user, algorithm='hybrid', limit=10):
    """ユーザーに合わせた推薦サークルを取得"""
    engine = CircleRecommendationEngine(user)
    return engine.get_recommendations(algorithm, limit)


def get_trending_circles(limit=10):
    """トレンドのサークルを取得"""
    # 最近のアクティビティを考慮してトレンドを計算
    recent_date = datetime.now() - timedelta(days=30)
    
    trending_circles = Circle.objects.filter(
        status='open'
    ).annotate(
        recent_posts=Count('posts', filter=Q(posts__created_at__gte=recent_date)),
        recent_members=Count('memberships', filter=Q(
            memberships__joined_at__gte=recent_date,
            memberships__status='active'
        ))
    ).order_by('-recent_posts', '-recent_members', '-member_count')[:limit]
    
    return trending_circles 