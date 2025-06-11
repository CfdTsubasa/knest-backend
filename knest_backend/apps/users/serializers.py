from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """
    ユーザー情報のシリアライザー
    """
    age = serializers.ReadOnlyField()  # 計算プロパティ
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'display_name', 'avatar_url',
            'bio', 'emotion_state', 'is_premium', 'last_active',
            'birth_date', 'prefecture', 'age',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'is_premium', 'last_active', 'age', 'created_at', 'updated_at']

class UserCreateSerializer(serializers.ModelSerializer):
    """
    ユーザー作成用のシリアライザー
    """
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'password', 'display_name',
            'avatar_url', 'bio', 'birth_date', 'prefecture'
        ]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            display_name=validated_data.get('display_name', ''),
            avatar_url=validated_data.get('avatar_url', ''),
            bio=validated_data.get('bio', ''),
            birth_date=validated_data.get('birth_date'),
            prefecture=validated_data.get('prefecture')
        )
        return user

class UserUpdateSerializer(serializers.ModelSerializer):
    """
    ユーザー情報更新用のシリアライザー
    """
    class Meta:
        model = User
        fields = [
            'display_name', 'avatar_url', 'bio',
            'emotion_state', 'birth_date', 'prefecture'
        ]

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'id': str(self.user.id),
            'username': self.user.username,
            'email': self.user.email,
            'display_name': self.user.display_name,
            'avatar_url': self.user.avatar_url or '',
            'bio': self.user.bio or '',
            'emotion_state': self.user.emotion_state or '',
            'birth_date': self.user.birth_date.isoformat() if self.user.birth_date else None,
            'prefecture': self.user.prefecture,
            'age': self.user.age,
            'is_premium': self.user.is_premium,
            'last_active': self.user.last_active.isoformat(),
            'created_at': self.user.created_at.isoformat(),
            'updated_at': self.user.updated_at.isoformat()
        }
        return data

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'display_name', 'birth_date', 'prefecture')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "パスワードが一致しません。"})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    age = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'display_name', 'avatar_url', 'bio', 
                 'emotion_state', 'birth_date', 'prefecture', 'age', 'is_premium', 'last_active', 'created_at')
        read_only_fields = ('id', 'username', 'age', 'is_premium', 'last_active', 'created_at')

class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password2 = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": "新しいパスワードが一致しません。"})
        return attrs

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password2 = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": "新しいパスワードが一致しません。"})
        return attrs 