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

from cars.views import *
from fuel_store.views import *
from users.views import *
from enterprises.views import *

from .yasg import urlpatterns as doc


r = DefaultRouter()

r.register(r"fuels", FuelViewSet, basename="fuel")
r.register(r"users", UserViewSet, basename="users")
r.register(r"achievements", AchievementViewSet, basename="achievements")
r.register(r"cars", CarViewSet, basename="cars")
r.register(r"orders", OrderViewSet, basename="orders")
r.register(r"wog_stations", WogViewSet, basename="wog")
r.register(r"okko_stations", OkkoViewSet, basename="okko")
r.register(r"ukrnafta_stations", UkrnaftaViewSet, basename="ukrnafta")
r.register(r"anp_stations", AnpViewSet, basename="anp")
r.register(r"companies", CompanyViewSet, basename="company")
r.register(r"services", CarServiceViewSet, basename="service")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(r.urls)),
    path("api-auth/", include("rest_framework.urls")),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("__debug__/", include("debug_toolbar.urls")),
    path("road/", RoadView.as_view(), name="road"),
    path("fuel_prices/", FuelPricesView.as_view()),
    path("fines/", FineView.as_view(), name="fines"),
    path("like_comment/<int:comment_id>/", CommentLike.as_view(), name="like_comment"),
    path("email_verificate/<token>/", EmailVerificateView.as_view(), name="email_verificate"),
    path("password_reset/", PasswordResetSendView.as_view(), name="password_reset_send"),
    path("password_reset/<uidb64>/<token>/", PasswordResetView.as_view(), name="password_reset"),
]

urlpatterns += doc

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
