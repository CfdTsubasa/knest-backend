from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import Circle, CircleInterest, CircleRecommendation, CircleMembership, Category, CirclePost, CircleEvent, CircleChat, CircleChatRead
from knest_backend.apps.users.serializers import UserSerializer
from knest_backend.apps.interests.serializers import InterestSerializer

class CircleInterestSerializer(serializers.ModelSerializer):
    """
    サークルと興味の関連のシリアライザー
    """
    interest = InterestSerializer(read_only=True)
    interest_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = CircleInterest
        fields = ['id', 'interest', 'interest_id', 'relevance_score', 'added_at']
        read_only_fields = ['id', 'added_at']

class CircleMembershipSerializer(serializers.ModelSerializer):
    """
    サークルメンバーシップのシリアライザー
    """
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = CircleMembership
        fields = [
            'id', 'user', 'circle', 'status', 'role',
            'joined_at', 'application_message', 'rejection_reason'
        ]
        read_only_fields = ['id', 'joined_at']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']

class CircleSerializer(serializers.ModelSerializer):
    """
    サークルのシリアライザー
    """
    owner = UserSerializer(read_only=True)
    interests = InterestSerializer(many=True, read_only=True)
    member_count = serializers.SerializerMethodField()
    is_member = serializers.SerializerMethodField()
    membership_status = serializers.SerializerMethodField()
    categories = CategorySerializer(many=True, read_only=True)
    post_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Circle
        fields = [
            'id', 'name', 'description', 'status', 'circle_type',
            'created_at', 'updated_at', 'owner', 'interests',
            'last_activity', 'member_count', 'is_member',
            'membership_status', 'categories', 'tags', 'post_count',
            'icon_url', 'cover_url', 'rules'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'last_activity',
            'member_count', 'is_member', 'membership_status', 'post_count'
        ]

    def get_member_count(self, obj):
        return obj.memberships.filter(status='active').count()

    def get_is_member(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.memberships.filter(
                user=request.user,
                status='active'
            ).exists()
        return False

    def get_membership_status(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                membership = obj.memberships.get(user=request.user)
                return membership.status
            except CircleMembership.DoesNotExist:
                return None
        return None

    def validate(self, data):
        if self.instance:
            # 既存のサークルを更新する場合
            if 'status' in data:
                member_count = self.instance.memberships.filter(
                    status='active'
                ).count()
                if data['status'] == 'open' and member_count >= 10:
                    raise serializers.ValidationError(
                        _('メンバーが10人以上いるため、募集を再開できません。')
                    )
        # カテゴリーの存在チェック
        categories = self.initial_data.get('categories', [])
        if not categories:
            raise serializers.ValidationError(_('少なくとも1つのカテゴリーを選択してください。'))
        return data

class CircleCreateSerializer(serializers.ModelSerializer):
    """
    サークル作成用のシリアライザー
    """
    interests = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Circle
        fields = [
            'name', 'description', 'is_premium',
            'member_limit', 'is_private', 'interests'
        ]

    def create(self, validated_data):
        interests = validated_data.pop('interests', [])
        circle = super().create(validated_data)
        
        for interest_id in interests:
            CircleInterest.objects.create(
                circle=circle,
                interest_id=interest_id
            )
        
        return circle

class CircleRecommendationSerializer(serializers.ModelSerializer):
    """
    サークルレコメンデーションのシリアライザー
    """
    circle = CircleSerializer(read_only=True)

    class Meta:
        model = CircleRecommendation
        fields = [
            'id', 'circle', 'recommendation_score',
            'recommendation_reason', 'created_at',
            'is_viewed'
        ]
        read_only_fields = ['id', 'created_at']

class CircleJoinRequestSerializer(serializers.Serializer):
    """サークル参加リクエストのシリアライザー"""
    application_message = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=1000
    )

class CircleJoinResponseSerializer(serializers.Serializer):
    """サークル参加申請への応答シリアライザー"""
    action = serializers.ChoiceField(choices=['approve', 'reject'])
    rejection_reason = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=1000
    )

    def validate(self, data):
        if data['action'] == 'reject' and not data.get('rejection_reason'):
            raise serializers.ValidationError(
                _('申請を拒否する場合は、理由を入力してください。')
            )
        return data

class CirclePostSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    class Meta:
        model = CirclePost
        fields = ['id', 'circle', 'author', 'content', 'media_urls', 'created_at', 'updated_at']

    def get_author(self, obj):
        return {
            'id': obj.author.id,
            'username': obj.author.username,
            'display_name': obj.author.display_name,
            'avatar_url': obj.author.avatar_url
        }

class CircleEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = CircleEvent
        fields = [
            'id', 'circle', 'title', 'description', 'start_datetime',
            'end_datetime', 'location', 'created_at', 'updated_at'
        ]

    def validate(self, data):
        if data['start_datetime'] >= data['end_datetime']:
            raise serializers.ValidationError(_('開始日時は終了日時より前である必要があります。'))
        return data

class CircleChatSerializer(serializers.ModelSerializer):
    """サークルチャットのシリアライザー"""
    sender = serializers.SerializerMethodField()
    reply_to = serializers.SerializerMethodField()
    read_by = serializers.SerializerMethodField()

    class Meta:
        model = CircleChat
        fields = [
            'id', 'circle', 'sender', 'content', 'media_urls',
            'created_at', 'updated_at', 'is_system_message',
            'is_edited', 'reply_to', 'read_by'
        ]
        read_only_fields = [
            'id', 'sender', 'created_at', 'updated_at',
            'is_edited', 'read_by'
        ]

    def get_sender(self, obj):
        return {
            'id': obj.sender.id,
            'username': obj.sender.username,
            'display_name': obj.sender.display_name,
            'avatar_url': obj.sender.avatar_url
        }

    def get_reply_to(self, obj):
        if obj.reply_to:
            return {
                'id': obj.reply_to.id,
                'content': obj.reply_to.content[:100],
                'sender': {
                    'id': obj.reply_to.sender.id,
                    'username': obj.reply_to.sender.username,
                    'display_name': obj.reply_to.sender.display_name
                }
            }
        return None

    def get_read_by(self, obj):
        reads = obj.circle.chat_reads.filter(
            last_read__gte=obj.created_at
        ).values('user__id', 'user__username', 'user__display_name')
        return [
            {
                'id': read['user__id'],
                'username': read['user__username'],
                'display_name': read['user__display_name']
            }
            for read in reads
        ]

class CircleChatReadSerializer(serializers.ModelSerializer):
    """チャット既読のシリアライザー"""
    class Meta:
        model = CircleChatRead
        fields = ['id', 'user', 'circle', 'last_read']
        read_only_fields = ['id', 'last_read'] 