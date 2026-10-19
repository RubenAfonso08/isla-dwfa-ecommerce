from decimal import Decimal

import pytest
from django.db import IntegrityError, transaction
from django.db.models import Count

from shop.factories import CategoryFactory, ProductFactory
from shop.models import Category, Product


@pytest.mark.django_db
def test_product_price_check_constraint():
    category = CategoryFactory()

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Product.objects.create(
                category=category,
                name="Produto com preço inválido",
                sku="INVALID-PRICE-001",
                price=Decimal("-1.00"),
                stock=1,
            )


@pytest.mark.django_db
def test_category_product_count_uses_at_most_two_queries(
    django_assert_max_num_queries,
):
    category = CategoryFactory()

    ProductFactory.create_batch(3, category=category)

    with django_assert_max_num_queries(2):
        categories = list(
            Category.objects.annotate(
                product_count=Count("products")
            ).order_by("name")
        )

    assert len(categories) == 1
    assert categories[0].product_count == 3


@pytest.mark.django_db
def test_failed_transaction_leaves_no_product():
    category = CategoryFactory()
    sku = "ROLLBACK-SKU-001"

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Product.objects.create(
                category=category,
                name="Produto temporário",
                sku=sku,
                price=Decimal("10.00"),
                stock=5,
            )

            # O segundo produto viola a constraint de SKU único.
            Product.objects.create(
                category=category,
                name="Produto duplicado",
                sku=sku,
                price=Decimal("15.00"),
                stock=3,
            )

    assert not Product.objects.filter(sku=sku).exists()