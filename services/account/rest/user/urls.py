from django.urls import path, include
from .views import UserViewSet
from rest_framework.routers import DefaultRouter

# --- Router for ViewSets ---
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
# --- End Router ---

urlpatterns = [
    path('', include(router.urls)),
]