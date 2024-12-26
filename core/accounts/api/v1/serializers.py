from rest_framework import serializers
from accounts.models import User
class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    def validate(self, attrs):
        if attrs.get('password1') != attrs.get('password2'):
            raise serializers.ValidationError('password and its confirmation should be the same')
        if User.objects.filter(email=attrs.get('email')).exists():
            raise serializers.ValidationError('a user with the same email already exists')
        return attrs
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(write_only=True)
    def validate(self, attrs):
        if not User.objects.filter(email=attrs.get('email')).exists():
            raise serializers.ValidationError('No user with given email was found')
        return attrs