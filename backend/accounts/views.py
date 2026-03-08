from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (
    AdminRegisterSerializer,
    AdminTokenObtainPairSerializer,
    UserRegisterSerializer,
    UserSerializer,
    UserTokenObtainPairSerializer,
)


class UserRegisterView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegisterSerializer


class AdminRegisterView(generics.CreateAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = AdminRegisterSerializer


class UserLoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserTokenObtainPairSerializer


class AdminLoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]
    serializer_class = AdminTokenObtainPairSerializer


class MeView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh = request.data.get("refresh")
        if not refresh:
            return Response({"detail": "refresh token required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh)
            token.blacklist()
        except Exception:
            return Response({"detail": "invalid refresh token"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)
