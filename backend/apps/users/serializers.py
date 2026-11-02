"""
User Serializers — Registration, login, and profile.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.validators import RegexValidator

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""

    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'password', 'password_confirm', 'phone',
        ]

    def validate_email(self, value):
        email = value.strip().casefold()
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError('A user with this email already exists.')
        return email

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError({'password_confirm': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone=validated_data.get('phone', ''),
            password=validated_data['password'],
        )
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile (read/update)."""

    is_admin = serializers.BooleanField(source='is_admin_user', read_only=True)
    pincode = serializers.CharField(required=False, allow_blank=True, validators=[RegexValidator(r'^\d{6}$', 'Enter a valid 6-digit postal code.')])

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'role', 'is_admin', 'phone', 'address', 'city', 'state', 'pincode',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'email', 'role', 'created_at', 'updated_at']


class UserListSerializer(serializers.ModelSerializer):
    """Serializer for admin user listing."""

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'role', 'is_superuser', 'is_active', 'phone', 'created_at',
        ]


class AdminUserStatusSerializer(serializers.ModelSerializer):
    """Allow admins to suspend or restore customer accounts without exposing credentials."""

    class Meta:
        model = User
        fields = ['is_active']

    def validate_is_active(self, value):
        user = self.instance
        request = self.context.get('request')
        if not value and user == getattr(request, 'user', None):
            raise serializers.ValidationError('You cannot deactivate your own account.')
        if user.is_superuser and not getattr(request.user, 'is_superuser', False):
            raise serializers.ValidationError('Only a superuser can change a superuser account.')
        return value
