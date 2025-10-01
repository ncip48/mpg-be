from django.urls import path
from .views import profile, LoginView, RefreshView

urlpatterns = [
    # Profile endpoint
    path('profile/', profile, name='user-profile'),

    # Auth endpoints
    path('login/', LoginView.as_view(), name='token_obtain_pair'),
    path('refresh/', RefreshView.as_view(), name='token_refresh'),
]