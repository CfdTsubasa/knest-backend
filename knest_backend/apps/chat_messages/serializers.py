from rest_framework import serializers
from .models import Message
from knest_backend.apps.users.serializers import UserSerializer

class MessageSerializer(serializers.ModelSerializer):
    """
    メッセージのシリアライザー
    """
    sender = UserSerializer(read_only=True)
    reply_to_message = serializers.SerializerMethodField()
    reaction_counts = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            'id', 'circle', 'sender', 'content',
            'message_type', 'emotion_tag', 'reply_to',
            'reply_to_message', 'created_at', 'updated_at',
            'reaction_counts'
        ]
        read_only_fields = ['id', 'sender', 'created_at', 'updated_at']

    def get_reply_to_message(self, obj):
        """返信先メッセージの基本情報を取得"""
        if obj.reply_to:
            return {
                'id': obj.reply_to.id,
                'content': obj.reply_to.content[:100],  # 最初の100文字のみ
                'sender': UserSerializer(obj.reply_to.sender).data
            }
        return None

    def get_reaction_counts(self, obj):
        """リアクションの種類ごとの数を取得"""
        return {
            reaction_type: obj.reactions.filter(reaction_type=reaction_type).count()
            for reaction_type, _ in obj.reactions.model.REACTION_TYPES
        }

    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)

class MessageCreateSerializer(serializers.ModelSerializer):
    """
    メッセージ作成用のシリアライザー
    """
    class Meta:
        model = Message
        fields = [
            'circle', 'content', 'message_type',
            'emotion_tag', 'reply_to'
        ]

    def validate_circle(self, value):
        """ユーザーがサークルのメンバーであることを確認"""
        user = self.context['request'].user
        if not value.memberships.filter(user=user).exists():
            raise serializers.ValidationError("このサークルのメンバーではありません。")
        return value 