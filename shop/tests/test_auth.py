import pytest
from django.contrib.auth.models import Group
from rest_framework.test import APIClient

from accounts.factories import UserFactory
from shop.factories import (
    CategoryFactory,
    CustomerFactory,
    OrderFactory,
)
from shop.models import Order


@pytest.fixture
def actors(db):
    gestor = UserFactory()
    gestor.groups.add(Group.objects.get(name="gestores"))

    return {
        "anon": None,
        "customer": UserFactory(),
        "gestor": gestor,
    }


def as_(user):
    api = APIClient()

    if user is not None:
        api.force_authenticate(user=user)

    return api


@pytest.mark.django_db
def test_orders_require_authentication():
    response = APIClient().get("/api/v1/orders/")

    assert response.status_code == 401


@pytest.mark.django_db
def test_login_returns_pair():
    user = UserFactory(username="ana")
    user.set_password("pass1234")
    user.save()

    response = APIClient().post(
        "/api/v1/auth/token/",
        {
            "username": "ana",
            "password": "pass1234",
        },
        format="json",
    )

    assert response.status_code == 200
    assert {"access", "refresh"} <= response.data.keys()


@pytest.mark.django_db
def test_refresh_rotates_and_blacklists_old_token():
    user = UserFactory()
    user.set_password("pass1234")
    user.save()

    client = APIClient()
    login = client.post(
        "/api/v1/auth/token/",
        {
            "username": user.username,
            "password": "pass1234",
        },
        format="json",
    )

    assert login.status_code == 200
    old_refresh = login.data["refresh"]

    refreshed = client.post(
        "/api/v1/auth/token/refresh/",
        {"refresh": old_refresh},
        format="json",
    )

    assert refreshed.status_code == 200
    assert "access" in refreshed.data
    assert "refresh" in refreshed.data

    reused = client.post(
        "/api/v1/auth/token/refresh/",
        {"refresh": old_refresh},
        format="json",
    )

    assert reused.status_code == 401


@pytest.mark.parametrize(
    ("role", "expected"),
    [
        ("anon", 401),
        ("customer", 403),
        ("gestor", 201),
    ],
)
def test_create_product_by_role(actors, role, expected):
    body = {
        "name": "Lamp",
        "sku": "LAMP-001",
        "price": "9.90",
        "stock": 3,
        "category": CategoryFactory().id,
    }

    response = as_(actors[role]).post(
        "/api/v1/products/",
        body,
        format="json",
    )

    assert response.status_code == expected


def test_customer_sees_only_own_orders(actors):
    customer = CustomerFactory(user=actors["customer"])
    own_order = OrderFactory(customer=customer)
    OrderFactory()

    response = as_(actors["customer"]).get("/api/v1/orders/")

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["id"] == own_order.id


def test_customer_cannot_retrieve_other_order(actors):
    other_order = OrderFactory()

    response = as_(actors["customer"]).get(f"/api/v1/orders/{other_order.id}/")

    assert response.status_code == 404


def test_customer_cannot_pay_other_order(actors):
    other_order = OrderFactory()

    response = as_(actors["customer"]).post(f"/api/v1/orders/{other_order.id}/pay/")

    assert response.status_code == 404


def test_manager_sees_all_orders(actors):
    OrderFactory()
    OrderFactory()

    response = as_(actors["gestor"]).get("/api/v1/orders/")

    assert response.status_code == 200
    assert response.data["count"] == 2


def test_customer_cannot_change_order_status(actors):
    customer = CustomerFactory(user=actors["customer"])
    order = OrderFactory(customer=customer)

    response = as_(actors["customer"]).patch(
        f"/api/v1/orders/{order.id}/",
        {"status": "paid"},
        format="json",
    )

    assert response.status_code == 200

    order.refresh_from_db()
    assert order.status == Order.Status.PENDING


def test_me_requires_authentication():
    response = APIClient().get("/api/v1/me/")

    assert response.status_code == 401


def test_me_returns_authenticated_user(actors):
    user = actors["customer"]

    response = as_(user).get("/api/v1/me/")

    assert response.status_code == 200
    assert response.data["id"] == user.pk
    assert response.data["username"] == user.username
    assert response.data["groups"] == []
