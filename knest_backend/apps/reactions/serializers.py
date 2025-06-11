from rest_framework import serializers
from .models import Reaction
from knest_backend.apps.users.serializers import UserSerializer

class ReactionSerializer(serializers.ModelSerializer):
    """
    リアクションのシリアライザー
    """
    user = UserSerializer(read_only=True)

    class Meta:
        model = Reaction
        fields = ['id', 'message', 'user', 'reaction_type', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def validate(self, attrs):
        """
        同じメッセージに対して同じユーザーが同じタイプのリアクションを
        複数回付けることを防ぐ
        """
        user = self.context['request'].user
        message = attrs['message']
        reaction_type = attrs['reaction_type']

        if Reaction.objects.filter(
            message=message,
            user=user,
            reaction_type=reaction_type
        ).exists():
            raise serializers.ValidationError(
                "このメッセージに対して既に同じリアクションを付けています。"
            )

        return attrs 