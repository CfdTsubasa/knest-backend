"""
次世代サークル推薦エンジン
階層型興味関心ベース推薦とマルチアルゴリズム統合
"""
import math
import logging
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional

from django.db import models
from django.db.models import Count, Q, Avg, F, Sum, Max
from django.core.cache import cache
from django.utils import timezone

from ..circles.models import Circle
from ..interests.models import UserInterestProfile, InterestCategory, InterestSubcategory, InterestTag
from ..users.models import User
from .models import UserRecommendationFeedback, UserSimilarity, UserInteractionHistory


logger = logging.getLogger(__name__)


class HierarchicalInterestMatcher:
    """階層型興味関心マッチングエンジン"""
    
    # レベルごとの重み
    LEVEL_WEIGHTS = {
        1: 0.3,  # カテゴリレベル
        2: 0.5,  # サブカテゴリレベル  
        3: 0.8,  # タグレベル
    }
    
    def __init__(self, user):
        self.user = user
        self.user_interests = self._get_user_hierarchical_interests()
    
    def _get_user_hierarchical_interests(self):
        """ユーザーの階層型興味関心を取得"""
        interests = UserInterestProfile.objects.filter(
            user=self.user
        ).select_related('category', 'subcategory', 'tag')
        
        hierarchical_data = {
            'categories': set(),
            'subcategories': set(), 
            'tags': set(),
            'level_data': {}
        }
        
        for interest in interests:
            hierarchical_data['categories'].add(interest.category.id)
            if interest.subcategory:
                hierarchical_data['subcategories'].add(interest.subcategory.id)
            if interest.tag:
                hierarchical_data['tags'].add(interest.tag.id)
            
            hierarchical_data['level_data'][interest.id] = {
                'level': interest.level,
                'category_id': interest.category.id,
                'subcategory_id': interest.subcategory.id if interest.subcategory else None,
                'tag_id': interest.tag.id if interest.tag else None,
            }
        
        return hierarchical_data
    
    def calculate_circle_match_score(self, circle):
        """サークルとの階層マッチングスコアを計算"""
        if not self.user_interests['level_data']:
            return 0.0
        
        # サークルの興味関心を取得（階層情報を含む）
        circle_interests = circle.interests.all()
        circle_categories = set()
        circle_subcategories = set()
        circle_tags = set()
        
        for interest in circle_interests:
            # 興味関心からカテゴリ/サブカテゴリ/タグ情報を抽出
            if hasattr(interest, 'category'):
                circle_categories.add(interest.category.id)
            if hasattr(interest, 'subcategory') and interest.subcategory:
                circle_subcategories.add(interest.subcategory.id)
            if hasattr(interest, 'tag') and interest.tag:
                circle_tags.add(interest.tag.id)
        
        total_score = 0.0
        max_possible_score = 0.0
        
        for interest_data in self.user_interests['level_data'].values():
            level = interest_data['level']
            weight = self.LEVEL_WEIGHTS[level]
            max_possible_score += weight
            
            # レベルに応じたマッチング
            if level == 1:  # カテゴリレベル
                if interest_data['category_id'] in circle_categories:
                    total_score += weight
            elif level == 2:  # サブカテゴリレベル
                if interest_data['subcategory_id'] in circle_subcategories:
                    total_score += weight
                elif interest_data['category_id'] in circle_categories:
                    total_score += weight * 0.5  # カテゴリマッチは半分の重み
            elif level == 3:  # タグレベル
                if interest_data['tag_id'] in circle_tags:
                    total_score += weight
                elif interest_data['subcategory_id'] in circle_subcategories:
                    total_score += weight * 0.6  # サブカテゴリマッチは0.6倍
                elif interest_data['category_id'] in circle_categories:
                    total_score += weight * 0.3  # カテゴリマッチは0.3倍
        
        return total_score / max_possible_score if max_possible_score > 0 else 0.0


class BehavioralRecommendationEngine:
    """行動ベース推薦エンジン"""
    
    def __init__(self, user):
        self.user = user
    
    def get_behavioral_preferences(self):
        """ユーザーの行動パターンから推薦を生成"""
        # 最近30日間の行動履歴を分析
        recent_date = timezone.now() - timedelta(days=30)
        
        interactions = UserInteractionHistory.objects.filter(
            user=self.user,
            created_at__gte=recent_date
        ).select_related('circle')
        
        # 行動パターン分析
        circle_scores = defaultdict(float)
        action_weights = {
            'view_circle': 1.0,
            'join_request': 5.0,
            'join_approved': 10.0,
            'post_message': 8.0,
            'react_to_post': 3.0,
            'join_event': 6.0,
        }
        
        for interaction in interactions:
            weight = action_weights.get(interaction.action_type, 1.0)
            circle_scores[interaction.circle.id] += weight
        
        # 時間減衰を適用
        for interaction in interactions:
            days_ago = (timezone.now() - interaction.created_at).days
            decay_factor = math.exp(-days_ago / 7.0)  # 7日で半減
            circle_scores[interaction.circle.id] *= decay_factor
        
        return dict(circle_scores)
    
    def recommend_similar_circles(self, limit=10):
        """行動履歴に基づく類似サークル推薦"""
        behavioral_prefs = self.get_behavioral_preferences()
        
        if not behavioral_prefs:
            return []
        
        # 高スコアサークルから類似サークルを発見
        top_circles = sorted(behavioral_prefs.items(), key=lambda x: x[1], reverse=True)[:5]
        top_circle_ids = [circle_id for circle_id, _ in top_circles]
        
        # 類似サークルを興味関心の重複で見つける
        similar_circles = Circle.objects.filter(
            status='open',
            interests__in=Circle.objects.filter(
                id__in=top_circle_ids
            ).values('interests')
        ).exclude(
            id__in=top_circle_ids
        ).exclude(
            memberships__user=self.user,
            memberships__status='active'
        ).annotate(
            interest_overlap=Count('interests')
        ).order_by('-interest_overlap', '-member_count')[:limit]
        
        return list(similar_circles)


class CollaborativeFilteringEngine:
    """改良された協調フィルタリングエンジン"""
    
    def __init__(self, user):
        self.user = user
    
    def find_similar_users(self, min_similarity=0.3, limit=50):
        """類似ユーザーを効率的に発見"""
        cache_key = f"similar_users_{self.user.id}_{min_similarity}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return cached_result
        
        # 共通の興味関心を持つユーザーを発見
        user_categories = set(
            UserInterestProfile.objects.filter(
                user=self.user
            ).values_list('category_id', flat=True)
        )
        
        if not user_categories:
            return []
        
        candidate_users = User.objects.filter(
            hierarchical_interests__category_id__in=user_categories
        ).exclude(
            id=self.user.id
        ).annotate(
            common_categories=Count(
                'hierarchical_interests__category',
                filter=Q(hierarchical_interests__category_id__in=user_categories)
            )
        ).filter(
            common_categories__gte=2
        ).order_by('-common_categories')[:limit * 2]
        
        # より詳細な類似度計算
        similar_users = []
        for candidate in candidate_users:
            similarity = self._calculate_user_similarity(candidate)
            if similarity >= min_similarity:
                similar_users.append((candidate, similarity))
        
        # 類似度順でソート
        similar_users.sort(key=lambda x: x[1], reverse=True)
        result = [user for user, _ in similar_users[:limit]]
        
        # 1時間キャッシュ
        cache.set(cache_key, result, 3600)
        return result
    
    def _calculate_user_similarity(self, other_user):
        """2ユーザー間の類似度を計算（コサイン類似度ベース）"""
        # キャッシュから取得を試行
        cache_key = f"user_sim_{min(self.user.id, other_user.id)}_{max(self.user.id, other_user.id)}"
        cached_sim = cache.get(cache_key)
        
        if cached_sim is not None:
            return cached_sim
        
        # 両ユーザーの興味関心ベクトルを作成
        user1_interests = self._get_user_interest_vector(self.user)
        user2_interests = self._get_user_interest_vector(other_user)
        
        # コサイン類似度計算
        similarity = self._cosine_similarity(user1_interests, user2_interests)
        
        # 30分キャッシュ
        cache.set(cache_key, similarity, 1800)
        return similarity
    
    def _get_user_interest_vector(self, user):
        """ユーザーの興味関心ベクトルを作成"""
        interests = UserInterestProfile.objects.filter(user=user)
        
        vector = defaultdict(float)
        for interest in interests:
            # レベルに応じた重み付け
            weight = HierarchicalInterestMatcher.LEVEL_WEIGHTS[interest.level]
            
            if interest.level == 1:
                vector[f"cat_{interest.category.id}"] = weight
            elif interest.level == 2 and interest.subcategory:
                vector[f"sub_{interest.subcategory.id}"] = weight
            elif interest.level == 3 and interest.tag:
                vector[f"tag_{interest.tag.id}"] = weight
        
        return vector
    
    def _cosine_similarity(self, vec1, vec2):
        """コサイン類似度を計算"""
        # 共通キーを取得
        common_keys = set(vec1.keys()) & set(vec2.keys())
        
        if not common_keys:
            return 0.0
        
        # ドット積
        dot_product = sum(vec1[key] * vec2[key] for key in common_keys)
        
        # ノルム計算
        norm1 = math.sqrt(sum(val**2 for val in vec1.values()))
        norm2 = math.sqrt(sum(val**2 for val in vec2.values()))
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def recommend_by_similar_users(self, limit=10):
        """類似ユーザーベースの推薦"""
        similar_users = self.find_similar_users()
        
        if not similar_users:
            return []
        
        # 類似ユーザーが参加しているサークルを推薦
        similar_user_ids = [user.id for user in similar_users[:20]]
        
        recommended_circles = Circle.objects.filter(
            memberships__user_id__in=similar_user_ids,
            memberships__status='active',
            status='open'
        ).exclude(
            memberships__user=self.user,
            memberships__status='active'
        ).annotate(
            similar_user_count=Count(
                'memberships__user',
                filter=Q(
                    memberships__user_id__in=similar_user_ids,
                    memberships__status='active'
                )
            )
        ).order_by('-similar_user_count', '-member_count')[:limit]
        
        return list(recommended_circles)


class LearningRecommendationEngine:
    """学習型推薦エンジン（フィードバック活用）"""
    
    def __init__(self, user):
        self.user = user
        self.feedback_weights = {
            'click': 1.0,
            'join_request': 3.0,
            'join_success': 5.0,
            'bookmark': 2.0,
            'dismiss': -1.0,
            'not_interested': -2.0,
        }
    
    def get_user_feedback_patterns(self):
        """ユーザーのフィードバックパターンを分析"""
        feedbacks = UserRecommendationFeedback.objects.filter(
            user=self.user,
            created_at__gte=timezone.now() - timedelta(days=60)
        ).select_related('circle')
        
        patterns = {
            'preferred_categories': defaultdict(float),
            'disliked_categories': defaultdict(float),
            'successful_algorithms': defaultdict(float),
            'avg_response_time': defaultdict(list),
        }
        
        for feedback in feedbacks:
            weight = self.feedback_weights.get(feedback.feedback_type, 0)
            
            # カテゴリ別の好み学習
            for interest in feedback.circle.interests.all():
                if hasattr(interest, 'category'):
                    if weight > 0:
                        patterns['preferred_categories'][interest.category.id] += weight
                    else:
                        patterns['disliked_categories'][interest.category.id] += abs(weight)
            
            # 有効なアルゴリズムの学習
            if weight > 0:
                patterns['successful_algorithms'][feedback.recommendation_algorithm] += weight
        
        return patterns
    
    def adjust_recommendations(self, recommendations):
        """フィードバックパターンに基づいて推薦結果を調整"""
        patterns = self.get_user_feedback_patterns()
        
        adjusted_recommendations = []
        for circle in recommendations:
            adjustment_factor = 1.0
            
            # カテゴリ別の好み反映
            for interest in circle.interests.all():
                if hasattr(interest, 'category'):
                    cat_id = interest.category.id
                    preferred_score = patterns['preferred_categories'].get(cat_id, 0)
                    disliked_score = patterns['disliked_categories'].get(cat_id, 0)
                    
                    if preferred_score > disliked_score:
                        adjustment_factor *= (1 + preferred_score * 0.1)
                    else:
                        adjustment_factor *= max(0.1, 1 - disliked_score * 0.1)
            
            adjusted_recommendations.append((circle, adjustment_factor))
        
        # 調整後のスコアでソート
        adjusted_recommendations.sort(key=lambda x: x[1], reverse=True)
        return [circle for circle, _ in adjusted_recommendations]


class NextGenRecommendationEngine:
    """次世代マルチアルゴリズム統合推薦エンジン"""
    
    def __init__(self, user):
        self.user = user
        self.hierarchical_matcher = HierarchicalInterestMatcher(user)
        self.behavioral_engine = BehavioralRecommendationEngine(user)
        self.collaborative_engine = CollaborativeFilteringEngine(user)
        self.learning_engine = LearningRecommendationEngine(user)
    
    def calculate_algorithm_weights(self):
        """ユーザー特性に応じた動的重み計算"""
        # デフォルト重み
        weights = {
            'hierarchical': 0.4,
            'collaborative': 0.3,
            'behavioral': 0.2,
            'diversity': 0.1
        }
        
        # ユーザープロファイル分析
        user_profile = self._analyze_user_profile()
        
        # 新規ユーザーはコンテンツベース重視
        if user_profile['is_new_user']:
            weights['hierarchical'] += 0.2
            weights['collaborative'] -= 0.2
        
        # アクティブユーザーは協調フィルタリング重視
        if user_profile['is_active_user']:
            weights['collaborative'] += 0.1
            weights['hierarchical'] -= 0.1
        
        # データが少ないユーザーは多様性重視
        if user_profile['has_limited_data']:
            weights['diversity'] += 0.1
            weights['behavioral'] -= 0.1
        
        return weights
    
    def _analyze_user_profile(self):
        """ユーザープロファイルを分析"""
        # 登録からの日数
        days_since_joined = (timezone.now() - self.user.date_joined).days
        
        # 興味関心の数
        interest_count = UserInterestProfile.objects.filter(user=self.user).count()
        
        # 最近の活動レベル
        recent_interactions = UserInteractionHistory.objects.filter(
            user=self.user,
            created_at__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        return {
            'is_new_user': days_since_joined < 7,
            'is_active_user': recent_interactions > 10,
            'has_limited_data': interest_count < 3,
            'days_since_joined': days_since_joined,
            'interest_count': interest_count,
            'recent_activity': recent_interactions,
        }
    
    def generate_recommendations(self, algorithm='smart', limit=10, diversity_factor=0.3):
        """統合推薦生成"""
        start_time = timezone.now()
        
        if algorithm == 'smart':
            weights = self.calculate_algorithm_weights()
        else:
            # 特定アルゴリズム
            weights = {
                'hierarchical': 1.0 if algorithm == 'content' else 0.0,
                'collaborative': 1.0 if algorithm == 'collaborative' else 0.0,
                'behavioral': 1.0 if algorithm == 'behavioral' else 0.0,
                'diversity': 0.0
            }
        
        # 各アルゴリズムから推薦取得
        hierarchical_results = self._get_hierarchical_recommendations(limit * 2)
        collaborative_results = self._get_collaborative_recommendations(limit * 2)
        behavioral_results = self._get_behavioral_recommendations(limit * 2)
        
        # 統合アルゴリズム
        integrated_scores = defaultdict(float)
        all_circles = set()
        
        # 階層型マッチング
        for circle, score in hierarchical_results:
            integrated_scores[circle.id] += score * weights['hierarchical']
            all_circles.add(circle)
        
        # 協調フィルタリング  
        for circle in collaborative_results:
            integrated_scores[circle.id] += 0.8 * weights['collaborative']
            all_circles.add(circle)
        
        # 行動ベース
        for circle in behavioral_results:
            integrated_scores[circle.id] += 0.7 * weights['behavioral']
            all_circles.add(circle)
        
        # 多様性保証
        if weights['diversity'] > 0:
            diverse_circles = self._ensure_diversity(list(all_circles), limit)
            for circle in diverse_circles:
                integrated_scores[circle.id] += 0.3 * weights['diversity']
        
        # 最終ランキング
        final_recommendations = sorted(
            all_circles,
            key=lambda c: integrated_scores[c.id],
            reverse=True
        )[:limit]
        
        # 学習型調整適用
        final_recommendations = self.learning_engine.adjust_recommendations(
            final_recommendations
        )
        
        # 推薦理由生成
        recommendations_with_reasons = []
        for circle in final_recommendations:
            reasons = self._generate_recommendation_reasons(
                circle, weights, integrated_scores[circle.id]
            )
            recommendations_with_reasons.append({
                'circle': circle,
                'score': integrated_scores[circle.id],
                'reasons': reasons,
                'confidence': min(integrated_scores[circle.id], 1.0),
            })
        
        computation_time = (timezone.now() - start_time).total_seconds() * 1000
        
        return {
            'recommendations': recommendations_with_reasons,
            'algorithm_weights': weights,
            'computation_time_ms': computation_time,
            'total_candidates': len(all_circles),
        }
    
    def _get_hierarchical_recommendations(self, limit):
        """階層型推薦結果を取得"""
        circles = Circle.objects.filter(status='open').exclude(
            memberships__user=self.user,
            memberships__status='active'
        ).prefetch_related('interests')
        
        scored_circles = []
        for circle in circles:
            score = self.hierarchical_matcher.calculate_circle_match_score(circle)
            if score > 0:
                scored_circles.append((circle, score))
        
        scored_circles.sort(key=lambda x: x[1], reverse=True)
        return scored_circles[:limit]
    
    def _get_collaborative_recommendations(self, limit):
        """協調フィルタリング推薦結果を取得"""
        return self.collaborative_engine.recommend_by_similar_users(limit)
    
    def _get_behavioral_recommendations(self, limit):
        """行動ベース推薦結果を取得"""
        return self.behavioral_engine.recommend_similar_circles(limit)
    
    def _ensure_diversity(self, circles, limit):
        """推薦結果の多様性を保証"""
        if not circles:
            return []
        
        # カテゴリ別にグループ化
        category_groups = defaultdict(list)
        for circle in circles:
            primary_category = circle.interests.first()
            if primary_category and hasattr(primary_category, 'category'):
                category_groups[primary_category.category.id].append(circle)
        
        # 各カテゴリから均等に選択
        diverse_selection = []
        max_per_category = max(1, limit // len(category_groups)) if category_groups else limit
        
        for group in category_groups.values():
            diverse_selection.extend(group[:max_per_category])
        
        return diverse_selection[:limit]
    
    def _generate_recommendation_reasons(self, circle, weights, score):
        """推薦理由を生成"""
        reasons = []
        
        # 階層マッチング理由
        if weights['hierarchical'] > 0:
            match_score = self.hierarchical_matcher.calculate_circle_match_score(circle)
            if match_score > 0.5:
                reasons.append({
                    'type': 'interest_match',
                    'detail': f'興味関心マッチ度: {match_score:.1%}',
                    'weight': weights['hierarchical']
                })
        
        # 協調フィルタリング理由
        if weights['collaborative'] > 0:
            similar_users = self.collaborative_engine.find_similar_users(limit=10)
            if similar_users:
                member_count = Circle.objects.filter(
                    id=circle.id,
                    memberships__user__in=similar_users,
                    memberships__status='active'
                ).count()
                
                if member_count > 0:
                    reasons.append({
                        'type': 'similar_users',
                        'detail': f'類似ユーザー{member_count}人が参加',
                        'weight': weights['collaborative']
                    })
        
        # 行動パターン理由
        if weights['behavioral'] > 0:
            behavioral_prefs = self.behavioral_engine.get_behavioral_preferences()
            if behavioral_prefs:
                reasons.append({
                    'type': 'activity_pattern',
                    'detail': '過去の活動パターンと一致',
                    'weight': weights['behavioral']
                })
        
        return reasons 