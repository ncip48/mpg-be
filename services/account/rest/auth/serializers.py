from __future__ import annotations
from typing import TYPE_CHECKING
from django.utils.translation import gettext_lazy as _
import logging
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer as BaseTokenObtainPairSerializer
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

from services.account.models.user import User

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = (
    "TokenObtainPairSerializer",
)

class TokenObtainPairSerializer(BaseTokenObtainPairSerializer):
    """
    Customizes the JWT token claims.
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # You can add custom claims to the token here if needed
        # For example: token['first_name'] = user.first_name
        return token

class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    """
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True, label="Confirm Password")

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        """
        Create and return a new user.
        """
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        # Use the set_password method to hash the password
        user.set_password(validated_data['password'])
        user.save()

        return user