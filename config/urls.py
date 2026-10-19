from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)
from rest_framework.routers import DefaultRouter

from core.views import health
from shop.views import (
    CategoryViewSet,
    CustomerViewSet,
    OrderItemViewSet,
    OrderViewSet,
    PaymentViewSet,
    ProductViewSet,
)


router = DefaultRouter()

router.register(
    "categories",
    CategoryViewSet,
    basename="category",
)
router.register(
    "products",
    ProductViewSet,
    basename="product",
)
router.register(
    "customers",
    CustomerViewSet,
    basename="customer",
)
router.register(
    "orders",
    OrderViewSet,
    basename="order",
)
router.register(
    "order-items",
    OrderItemViewSet,
    basename="order-item",
)
router.register(
    "payments",
    PaymentViewSet,
    basename="payment",
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health, name="health"),

    # API REST versionada
    path("api/v1/", include(router.urls)),

    # Documentação OpenAPI e interface Swagger
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]