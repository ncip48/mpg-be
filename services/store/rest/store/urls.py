from django.urls import path, include
from .views import StoreViewSet
from rest_framework.routers import DefaultRouter

# --- Router for ViewSets ---
router = DefaultRouter()
router.register(r'stores', StoreViewSet, basename='store')
# --- End Router ---

urlpatterns = [
    path('', include(router.urls)),
]