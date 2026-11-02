"""
User Views — Registration, profile, and JWT auth endpoints.
"""

from rest_framework import generics, status, filters
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.contrib.auth import get_user_model

from apps.users.permissions import IsAdminUser
from .serializers import (
    AdminUserStatusSerializer,
    UserListSerializer,
    UserRegistrationSerializer,
    UserProfileSerializer,
)

User = get_user_model()


def _set_refresh_cookie(response, token):
    lifetime = settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']
    response['Cache-Control'] = 'no-store'
    response['Pragma'] = 'no-cache'
    response.set_cookie(
        settings.JWT_REFRESH_COOKIE_NAME,
        token,
        max_age=int(lifetime.total_seconds()),
        httponly=True,
        secure=settings.JWT_COOKIE_SECURE,
        samesite=settings.JWT_COOKIE_SAMESITE,
        path='/api/auth/',
    )
    return response


def _clear_refresh_cookie(response):
    response['Cache-Control'] = 'no-store'
    response['Pragma'] = 'no-cache'
    response.delete_cookie(
        settings.JWT_REFRESH_COOKIE_NAME,
        path='/api/auth/',
        samesite=settings.JWT_COOKIE_SAMESITE,
    )
    return response


def _origin_is_allowed(request):
    origin = request.headers.get('Origin')
    return not origin or origin in settings.CORS_ALLOWED_ORIGINS


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        attrs[self.username_field] = attrs[self.username_field].strip().casefold()
        return super().validate(attrs)


class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'auth_login'

    def post(self, request):
        if not _origin_is_allowed(request):
            return Response({'success': False, 'error': {'code': 'ORIGIN_NOT_ALLOWED', 'message': 'Request origin is not allowed.'}}, status=status.HTTP_403_FORBIDDEN)
        serializer = EmailTokenObtainPairSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response = Response({
            'success': True,
            'data': {'access': serializer.validated_data['access']},
        })
        return _set_refresh_cookie(response, serializer.validated_data['refresh'])


class CookieTokenRefreshView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'auth_refresh'

    def post(self, request):
        if not _origin_is_allowed(request):
            return Response({'success': False, 'error': {'code': 'ORIGIN_NOT_ALLOWED', 'message': 'Request origin is not allowed.'}}, status=status.HTTP_403_FORBIDDEN)
        refresh = request.COOKIES.get(settings.JWT_REFRESH_COOKIE_NAME)
        if not refresh:
            response = Response({'success': False, 'error': {'code': 'AUTHENTICATION_REQUIRED', 'message': 'Sign in again to continue.'}}, status=status.HTTP_401_UNAUTHORIZED)
            return _clear_refresh_cookie(response)
        serializer = TokenRefreshSerializer(data={'refresh': refresh})
        try:
            serializer.is_valid(raise_exception=True)
        except InvalidToken:
            response = Response({'success': False, 'error': {'code': 'AUTHENTICATION_REQUIRED', 'message': 'Sign in again to continue.'}}, status=status.HTTP_401_UNAUTHORIZED)
            return _clear_refresh_cookie(response)
        response = Response({'success': True, 'data': {'access': serializer.validated_data['access']}})
        rotated = serializer.validated_data.get('refresh')
        return _set_refresh_cookie(response, rotated or refresh)


class RegisterView(generics.CreateAPIView):
    """User registration endpoint."""

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'auth_register'

    def create(self, request, *args, **kwargs):
        if not _origin_is_allowed(request):
            return Response({'success': False, 'error': {'code': 'ORIGIN_NOT_ALLOWED', 'message': 'Request origin is not allowed.'}}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate tokens for immediate login
        refresh = RefreshToken.for_user(user)

        response = Response({
            'success': True,
            'message': 'Registration successful.',
            'data': {
                'user': UserProfileSerializer(user).data,
                'access': str(refresh.access_token),
            },
        }, status=status.HTTP_201_CREATED)
        return _set_refresh_cookie(response, str(refresh))


class ProfileView(generics.RetrieveUpdateAPIView):
    """Get or update current user profile."""

    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return Response({
            'success': True,
            'data': serializer.data,
        })

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(request.user, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'success': True,
            'message': 'Profile updated successfully.',
            'data': serializer.data,
        })


class LogoutView(APIView):
    """Logout by blacklisting the refresh token."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not _origin_is_allowed(request):
            return Response({'success': False, 'error': {'code': 'ORIGIN_NOT_ALLOWED', 'message': 'Request origin is not allowed.'}}, status=status.HTTP_403_FORBIDDEN)
        try:
            refresh_token = request.COOKIES.get(settings.JWT_REFRESH_COOKIE_NAME)
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            response = Response({
                'success': True,
                'message': 'Logged out successfully.',
            }, status=status.HTTP_200_OK)
            return _clear_refresh_cookie(response)
        except Exception:
            response = Response({
                'success': False,
                'error': {
                    'code': 'INVALID_TOKEN',
                    'message': 'Invalid or expired token.',
                },
            }, status=status.HTTP_400_BAD_REQUEST)
            return _clear_refresh_cookie(response)


class AdminUserListView(generics.ListAPIView):
    """Searchable user directory for administrators."""

    serializer_class = UserListSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering_fields = ['created_at', 'email']
    ordering = ['-created_at']

    def get_queryset(self):
        return User.objects.all().order_by('-created_at', '-pk')


class AdminUserStatusView(generics.UpdateAPIView):
    """Admin-only account activation control; user records are never hard-deleted here."""

    serializer_class = AdminUserStatusSerializer
    permission_classes = [IsAdminUser]
    queryset = User.objects.all()
    http_method_names = ['patch', 'head', 'options']

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'success': True,
            'message': 'User access updated.',
            'data': UserListSerializer(instance).data,
        })
