"""
URL configuration for drive_hub project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from drive_hub.yasg import urlpatterns as doc

from users.views import (
    AchievementViewSet, 
    UserViewSet,
    PasswordResetLinkAPIView, 
    PasswordResetAPIView,
    RouteAPIView,
    EmailVerificateAPIView,
    CommentLikeAPIView,
    CommentDeleteAPIView
)
from fuels.views import (
    FuelViewSet,
    OrderViewSet,
    WogAPIView,
    OkkoAPIView,
    UkrnaftaAPIView,
    AnpAPIView,
    FuelPricesAPIView,
)
from cars.views import CarViewSet, FineViewSet
from enterprises.views import CompanyViewSet, CarServiceViewSet


r = DefaultRouter()
# users viewsets
r.register(r'users', UserViewSet, basename='users')
r.register(r'achievements', AchievementViewSet, basename='achievements')

# fuels viewsets
r.register(r'fuels', FuelViewSet, basename='fuels')
r.register(r'orders', OrderViewSet, basename='orders')

# cars viewsets
r.register(r'cars', CarViewSet, basename='cars')
r.register(r'fines', FineViewSet, basename='fines')

# enterprises viewsets
r.register(r'companies', CompanyViewSet, basename='company')
r.register(r'services', CarServiceViewSet, basename='service')


urlpatterns = [
    path('', include(r.urls)),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('__debug__/', include('debug_toolbar.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Stations views
    path('wog-stations/', WogAPIView.as_view(), name='wog_stations'),
    path('okko-stations/', OkkoAPIView.as_view(), name='okko_stations'),
    path('ukrnafta-stations/', UkrnaftaAPIView.as_view(), name='ukrnafta_stations'),
    path('anp-stations/', AnpAPIView.as_view(), name='anp_stations'),

    # Custom views
    path('routes/', RouteAPIView.as_view(), name='routes'),
    path('fuel-prices/', FuelPricesAPIView.as_view()),
    path('delete-comment/<int:comment_id>/', CommentDeleteAPIView.as_view(), name='delete_comment'),
    path('like-comment/<int:comment_id>/', CommentLikeAPIView.as_view(), name='like_comment'),
    path('email-verificate/<token>/', EmailVerificateAPIView.as_view(), name='email_verificate'),
    path('password-reset/', PasswordResetLinkAPIView.as_view(), name='password_reset_link'),
    path('password-reset/<uidb64>/<token>/', PasswordResetAPIView.as_view(), name='password_reset'),
]

urlpatterns += doc

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
