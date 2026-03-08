from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "username", "email", "role", "is_staff", "is_superuser")

    def get_role(self, obj):
        return "admin" if obj.is_staff else "user"


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password")

    def create(self, validated_data):
        user = User(
            username=validated_data.get("username"),
            email=validated_data.get("email", ""),
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class UserRegisterSerializer(RegisterSerializer):
    def create(self, validated_data):
        user = User(
            username=validated_data.get("username"),
            email=validated_data.get("email", ""),
            is_staff=False,
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class AdminRegisterSerializer(RegisterSerializer):
    def create(self, validated_data):
        user = User(
            username=validated_data.get("username"),
            email=validated_data.get("email", ""),
            is_staff=True,
            is_superuser=False,
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class RoleTokenObtainPairSerializer(TokenObtainPairSerializer):
    role = "user"

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        if self.role == "admin":
            if not user.is_staff:
                raise AuthenticationFailed("Admin account required.")
        else:
            if user.is_staff:
                raise AuthenticationFailed("Please use the admin login endpoint.")
        return data


class UserTokenObtainPairSerializer(RoleTokenObtainPairSerializer):
    role = "user"


class AdminTokenObtainPairSerializer(RoleTokenObtainPairSerializer):
    role = "admin"
