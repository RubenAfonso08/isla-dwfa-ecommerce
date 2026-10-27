from decimal import Decimal

from django.core.management.base import BaseCommand

from accounts.factories import UserFactory
from shop.factories import (
    CategoryFactory,
    CustomerFactory,
    OrderFactory,
    OrderItemFactory,
    PaymentFactory,
    ProductFactory,
)
from shop.models import Order


class Command(BaseCommand):
    help = "Cria dados de demonstração para a loja sem duplicar registos."

    def handle(self, *args, **options):
        # Categorias
        technology = CategoryFactory(
            slug="tecnologia",
            name="Tecnologia",
            description="Equipamentos eletrónicos",
        )

        accessories = CategoryFactory(
            slug="acessorios",
            name="Acessórios",
            description="Acessórios para computadores",
        )

        # Produtos
        laptop = ProductFactory(
            sku="SKU-LAPTOP-001",
            category=technology,
            name="Computador portátil",
            price=Decimal("899.90"),
            stock=10,
        )

        mouse = ProductFactory(
            sku="SKU-MOUSE-001",
            category=accessories,
            name="Rato sem fios",
            price=Decimal("14.90"),
            stock=50,
        )

        ProductFactory(
            sku="SKU-MONITOR-001",
            category=technology,
            name="Monitor",
            price=Decimal("179.90"),
            stock=15,
        )

        # Cliente
        user = UserFactory(
            username="cliente_demo",
            email="cliente.demo@example.com",
        )

        customer = CustomerFactory(
            user=user,
            phone="",
            address="Rua de Demonstração, Porto",
        )

        # Encomenda
        order = OrderFactory(
            reference="ORD-SEED-001",
            customer=customer,
            status=Order.Status.PENDING,
            shipping_address=customer.address,
        )

        # Artigos da encomenda
        OrderItemFactory(
            order=order,
            product=laptop,
            quantity=1,
            unit_price=laptop.price,
        )

        OrderItemFactory(
            order=order,
            product=mouse,
            quantity=2,
            unit_price=mouse.price,
        )

        # Calcular o total dos artigos da encomenda
        total = sum(
            (
                quantity * unit_price
                for quantity, unit_price in order.items.values_list(
                    "quantity",
                    "unit_price",
                )
            ),
            Decimal("0.00"),
        )

        # Pagamento de demonstração
        PaymentFactory(
            order=order,
            amount=total,
            provider="demo",
            status="pending",
        )

        self.stdout.write(
            self.style.SUCCESS("Seed concluído. Dados de demonstração confirmados ou criados.")
        )
