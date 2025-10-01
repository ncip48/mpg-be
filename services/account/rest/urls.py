from django.urls import path, include
from .auth import urls as auth_urls
from .permission import urls as permission_urls
from .role import urls as role_urls
from .user import urls as user_urls

app_name = "account"

urlpatterns = [
    path('auth/', include(auth_urls)),
    path('permission/', include(permission_urls)),
    path('role/', include(role_urls)),
    path('user/', include(user_urls)),
]