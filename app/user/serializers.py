from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializers for the user object"""

    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'name')
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 5}
        }

    def create(self, validated_data):
        """ create and return user with encrypted password"""
        return get_user_model().objects.create_user(**validated_data)


class AuthTokenSerializer(serializers.Serializer):
    """user authentication serializer"""
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """authenticate a user"""
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(request=self.context.get('request'),
                            username=email,
                            password=password
                            )
        if not user:
            message = _('Invalid credentials')
            raise serializers.ValidationError(message, code='authentication')
        
        attrs['user'] = user
        return attrs
