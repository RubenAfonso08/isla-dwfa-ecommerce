from decimal import Decimal

from rest_framework import serializers

from .models import (
    Category,
    Customer,
    Order,
    OrderItem,
    Payment,
    Product,
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(
        source="category.name",
        read_only=True,
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "sku",
            "name",
            "price",
            "stock",
            "category",
            "category_name",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "category_name"]

    def validate_price(self, value):
        """Valida o preço de um produto."""
        if value < Decimal("0.00"):
            raise serializers.ValidationError("O preço não pode ser negativo.")

        return value


class CustomerSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        source="user.username",
        read_only=True,
    )
    email = serializers.EmailField(
        source="user.email",
        read_only=True,
    )

    class Meta:
        model = Customer
        fields = [
            "id",
            "username",
            "email",
            "phone",
            "address",
            "created_at",
        ]
        read_only_fields = fields


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(
        source="product.name",
        read_only=True,
    )

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "order",
            "product",
            "product_name",
            "quantity",
            "unit_price",
        ]
        read_only_fields = ["id", "product_name", "unit_price"]

    def validate_quantity(self, value):
        """Valida a quantidade de um artigo."""
        if value <= 0:
            raise serializers.ValidationError("A quantidade tem de ser superior a zero.")

        return value

    def validate(self, attrs):
        """
        Aplica regras que dependem de vários campos da encomenda.
        """
        order = attrs.get("order", getattr(self.instance, "order", None))
        product = attrs.get(
            "product",
            getattr(self.instance, "product", None),
        )
        quantity = attrs.get(
            "quantity",
            getattr(self.instance, "quantity", None),
        )

        errors = {}

        if order and order.status != Order.Status.PENDING:
            errors["order"] = "Só é possível adicionar artigos a encomendas pendentes."

        if product and not product.is_active:
            errors["product"] = "O produto não está ativo."

        if product and quantity is not None and quantity > product.stock:
            errors["quantity"] = (
                f"Stock insuficiente. Existem apenas {product.stock} unidades disponíveis."
            )

        if errors:
            raise serializers.ValidationError(errors)

        return attrs

    def create(self, validated_data):
        """
        O preço unitário é definido pelo servidor, no momento da criação.
        O cliente não pode escolher o preço enviado à API.
        """
        validated_data["unit_price"] = validated_data["product"].price

        return super().create(validated_data)


class OrderSerializer(serializers.ModelSerializer):
    customer_username = serializers.CharField(
        source="customer.user.username",
        read_only=True,
    )

    # Os artigos são apresentados aninhados na representação da encomenda.
    items = OrderItemSerializer(many=True, read_only=True)

    # O total é fornecido pelo queryset, que faz o cálculo na base de dados.
    total = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "reference",
            "customer",
            "customer_username",
            "status",
            "shipping_address",
            "items",
            "total",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "customer",
            "status",
            "customer_username",
            "items",
            "total",
            "created_at",
            "updated_at",
        ]


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id",
            "order",
            "amount",
            "status",
            "provider",
            "transaction_reference",
            "created_at",
        ]
        read_only_fields = fields
