from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from shop.factories import (
    OrderFactory,
    OrderItemFactory,
    ProductFactory,
)
from shop.models import OrderItem


@pytest.mark.django_db
def test_order_list_is_paginated_without_n_plus_one(
    django_assert_max_num_queries,
):
    # Criadas 25 encomendas, cada uma com 3 artigos.
    for order in OrderFactory.create_batch(25):
        OrderItemFactory.create_batch(3, order=order)

    client = APIClient()

    # COUNT + encomendas + artigos (com os produtos relacionados).
    with django_assert_max_num_queries(3):
        response = client.get("/api/v1/orders/")

    assert response.status_code == 200

    body = response.json()

    assert body["count"] == 25
    assert len(body["results"]) == 20

    # Confirma que os artigos e os nomes dos produtos estão aninhados.
    assert body["results"][0]["items"][0]["product_name"]


@pytest.mark.django_db
def test_create_order_item_returns_201_and_saves_price():
    order = OrderFactory()
    product = ProductFactory(
        stock=10,
        price=Decimal("19.90"),
    )

    client = APIClient()

    response = client.post(
        "/api/v1/order-items/",
        {
            "order": order.pk,
            "product": product.pk,
            "quantity": 2,
        },
        format="json",
    )

    assert response.status_code == 201

    item = OrderItem.objects.get(
        order=order,
        product=product,
    )

    assert item.quantity == 2
    assert item.unit_price == Decimal("19.90")
    assert response.data["unit_price"] == "19.90"


@pytest.mark.django_db
def test_create_order_item_with_insufficient_stock_returns_400():
    order = OrderFactory()
    product = ProductFactory(stock=1)

    client = APIClient()

    response = client.post(
        "/api/v1/order-items/",
        {
            "order": order.pk,
            "product": product.pk,
            "quantity": 2,
        },
        format="json",
    )

    assert response.status_code == 400
    assert "errors" in response.data
    assert "quantity" in response.data["errors"]

    assert not OrderItem.objects.filter(
        order=order,
        product=product,
    ).exists()