from decimal import Decimal

from django.db.models import (
    DecimalField,
    ExpressionWrapper,
    F,
    Prefetch,
    Sum,
    Value,
)
from django.db.models.functions import Coalesce
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import ProductFilter
from .models import (
    Category,
    Customer,
    Order,
    OrderItem,
    Payment,
    Product,
)
from .permissions import (
    IsGestor,
    IsGestorOrReadOnly,
    IsOwnerOrGestor,
    is_gestor,
)
from .serializers import (
    CategorySerializer,
    CustomerSerializer,
    OrderItemSerializer,
    OrderSerializer,
    PaymentSerializer,
    ProductSerializer,
)
from .services import pay_order


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    filterset_fields = ["is_active"]
    search_fields = ["name", "slug"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]

    permission_classes = [IsGestorOrReadOnly]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related("category")
    serializer_class = ProductSerializer

    filterset_class = ProductFilter
    search_fields = ["name", "sku"]
    ordering_fields = ["price", "name", "created_at"]
    ordering = ["name"]

    permission_classes = [IsGestorOrReadOnly]


class CustomerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Customer.objects.select_related("user")
    serializer_class = CustomerSerializer

    search_fields = ["user__username", "user__email"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]

    permission_classes = [IsGestor]


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.select_related(
        "order",
        "product",
    )
    serializer_class = OrderItemSerializer

    filterset_fields = ["order", "product"]

    # Os artigos podem ser consultados e criados, mas não atualizados
    # ou eliminados diretamente nesta versão da API.
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if not user.is_authenticated:
            return queryset.none()

        if is_gestor(user):
            return queryset

        return queryset.filter(order__customer__user=user)

    def perform_create(self, serializer):
        order = serializer.validated_data["order"]
        user = self.request.user

        if not is_gestor(user) and order.customer.user_id != user.id:
            raise NotFound()

        serializer.save()


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer

    filterset_fields = ["status", "customer"]
    search_fields = ["reference", "customer__user__username"]
    ordering_fields = ["created_at", "total"]
    ordering = ["-created_at", "-pk"]

    permission_classes = [IsAuthenticated, IsOwnerOrGestor]

    def get_queryset(self):
        line_total = ExpressionWrapper(
            F("items__quantity") * F("items__unit_price"),
            output_field=DecimalField(
                max_digits=12,
                decimal_places=2,
            ),
        )

        item_queryset = OrderItem.objects.select_related("product")

        queryset = (
            Order.objects.select_related("customer__user")
            .prefetch_related(Prefetch("items", queryset=item_queryset))
            .annotate(
                total=Coalesce(
                    Sum(line_total),
                    Value(Decimal("0.00")),
                    output_field=DecimalField(
                        max_digits=12,
                        decimal_places=2,
                    ),
                )
            )
            .order_by("-created_at", "-pk")
        )

        user = self.request.user

        if not user.is_authenticated:
            return queryset.none()

        if is_gestor(user):
            return queryset

        return queryset.filter(customer__user=user)

    def perform_create(self, serializer):
        customer, _ = Customer.objects.get_or_create(user=self.request.user)

        serializer.save(customer=customer)

    @extend_schema(
        request=None,
        responses={
            200: OrderSerializer,
            409: OpenApiResponse(description=("A encomenda não pode ser paga no estado atual.")),
        },
        summary="Pagar uma encomenda pendente",
        description=(
            "Regista o pagamento de demonstração e altera o estado da encomenda para pago."
        ),
    )
    @action(detail=True, methods=["post"])
    def pay(self, request, pk=None):
        order = self.get_object()
        paid_order = pay_order(order)

        # Recarrega a representação com o total e os artigos aninhados.
        paid_order = self.get_queryset().get(pk=paid_order.pk)

        return Response(self.get_serializer(paid_order).data)


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Payment.objects.select_related("order")
    serializer_class = PaymentSerializer

    filterset_fields = ["status", "provider", "order"]
    ordering_fields = ["amount", "created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if not user.is_authenticated:
            return queryset.none()

        if is_gestor(user):
            return queryset

        return queryset.filter(order__customer__user=user)
