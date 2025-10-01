from __future__ import annotations
from typing import TYPE_CHECKING
from django.utils.translation import gettext_lazy as _
import logging
from rest_framework import permissions
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from services.account.rest.user.serializers import ProfileSerializer
from .serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = (
    "profile",
    "LoginView",
    "RefreshView",
)

@swagger_auto_schema(
    method="get",
    tags=["User"],
    operation_id="profile",
    operation_description="Retrieve current user profile"
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def profile(request):
    """
    Retrieve the profile of the currently authenticated user.
    """
    user = request.user
    serializer = ProfileSerializer(user)
    return Response(serializer.data)


class LoginView(TokenObtainPairView):
    """
    Login endpoint that returns JWT access and refresh tokens.
    """
    permission_classes = (AllowAny,)
    serializer_class = TokenObtainPairSerializer
    
    @swagger_auto_schema(
        tags=["Auth"],
        operation_id="login",
        operation_description="Login endpoint that returns JWT access and refresh tokens.",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
    
class RefreshView(TokenRefreshView):
    """
    Refresh endpoint that returns a new JWT access token using a refresh token.
    """
    permission_classes = (AllowAny,)
    serializer_class = TokenRefreshSerializer

    @swagger_auto_schema(
        tags=["Auth"],
        operation_id="refresh_token",
        operation_description="Refresh endpoint that returns a new JWT access token using a refresh token.",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)