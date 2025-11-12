from django.conf import settings
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from portfolio.views import HoldingViewSet, PortfolioViewSet

from .views import health

router = DefaultRouter()
router.register(r"portfolios", PortfolioViewSet, basename="portfolio")
router.register(r"holdings", HoldingViewSet, basename="holding")

urlpatterns = [
    path("health/", health),
    path("api/v1/", include(router.urls)),
    path("api/v1/", include("users.urls")),
]

# Serve docs only when DEBUG=True (local/staging)
if settings.DEBUG:
    from drf_spectacular.views import (
        SpectacularAPIView,
        SpectacularRedocView,
        SpectacularSwaggerView,
    )

    urlpatterns += [
        path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
        path(
            "api/docs/",
            SpectacularSwaggerView.as_view(url_name="schema"),
            name="swagger-ui",
        ),
        path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    ]
