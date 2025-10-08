"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.conf.urls.static import static

from core import settings

# --- Swagger/OpenAPI Configuration ---
schema_view = get_schema_view(
    openapi.Info(
        title="Convection API",
        default_version="v1",
        description="API documentation for the Convection Production Workflow application.",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@convection.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    # url="http://localhost:8080/api",
)
# --- End Swagger Configuration ---

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('services.account.rest.urls')),
    path('api/', include('services.printer.rest.urls')),
    path('api/', include('services.store.rest.urls')),
    path('api/', include('services.product.rest.urls')),
    path('api/', include('services.customer.rest.urls')),
    
    # Swagger UI routes
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
    
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# if settings.DEBUG:
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)