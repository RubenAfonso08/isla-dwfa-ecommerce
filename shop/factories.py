from decimal import Decimal

import factory

from accounts.factories import UserFactory

from .models import Category, Customer, Order, OrderItem, Payment, Product


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category
        django_get_or_create = ("slug",)

    name = factory.Sequence(lambda n: f"Categoria {n:04d}")
    slug = factory.Sequence(lambda n: f"categoria-{n:04d}")
    description = "Categoria de demonstração"
    is_active = True


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product
        django_get_or_create = ("sku",)

    category = factory.SubFactory(CategoryFactory)
    name = factory.Sequence(lambda n: f"Produto {n:04d}")
    sku = factory.Sequence(lambda n: f"SKU-{n:06d}")
    price = factory.LazyFunction(lambda: Decimal("19.90"))
    stock = 10
    is_active = True


class CustomerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Customer
        django_get_or_create = ("user",)

    user = factory.SubFactory(UserFactory)
    phone = ""
    address = "Rua de Teste, Porto"


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order
        django_get_or_create = ("reference",)

    reference = factory.Sequence(lambda n: f"ORD-{n:06d}")
    customer = factory.SubFactory(CustomerFactory)
    status = Order.Status.PENDING
    shipping_address = "Rua de Teste, Porto"


class OrderItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrderItem
        django_get_or_create = ("order", "product")

    order = factory.SubFactory(OrderFactory)
    product = factory.SubFactory(ProductFactory)
    quantity = 1
    unit_price = factory.LazyAttribute(lambda obj: obj.product.price)


class PaymentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Payment
        django_get_or_create = ("order",)

    order = factory.SubFactory(OrderFactory)
    amount = factory.LazyAttribute(
        lambda obj: sum(
            (item.quantity * item.unit_price for item in obj.order.items.all()),
            Decimal("0.00"),
        )
    )
    status = Payment.Status.PENDING
    provider = "demo"
    transaction_reference = ""
