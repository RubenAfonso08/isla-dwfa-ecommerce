from decimal import Decimal
from unittest.mock import patch

import pytest
from django.contrib.auth.models import Group
from django.core import mail
from django.core.cache import cache
from django.test import TestCase
from rest_framework.test import APIClient

from accounts.factories import UserFactory
from shop.factories import (
    CustomerFactory,
    OrderFactory,
    OrderItemFactory,
    PaymentFactory,
)
from shop.models import Order, Payment
from shop.services import pay_order
from shop.tasks import export_orders_report, send_order_receipt


class TestOrderReceiptScheduling(TestCase):
    def test_receipt_is_idempotent(self):
        order = OrderFactory(status=Order.Status.PAID)

        PaymentFactory(
            order=order,
            amount=Decimal("25.00"),
            status=Payment.Status.COMPLETED,
        )

        mail.outbox.clear()

        first_result = send_order_receipt.run(order.pk)
        second_result = send_order_receipt.run(order.pk)

        payment = order.payment
        payment.refresh_from_db()

        assert first_result == "sent"
        assert second_result == "already-sent"
        assert payment.receipt_sent_at is not None

        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == [order.customer.user.email]
        assert order.reference in mail.outbox[0].subject

    def test_pay_schedules_receipt_after_commit(self):
        order = OrderFactory()

        OrderItemFactory(
            order=order,
            quantity=2,
            unit_price=Decimal("12.50"),
        )

        with patch("shop.services.send_order_receipt.delay") as delay_mock:
            with self.captureOnCommitCallbacks(execute=True) as callbacks:
                paid_order = pay_order(order)

            assert len(callbacks) == 1
            delay_mock.assert_called_once_with(paid_order.pk)

        paid_order.refresh_from_db()

        assert paid_order.status == Order.Status.PAID
        assert paid_order.payment.status == Payment.Status.COMPLETED


@pytest.mark.django_db
def test_orders_report_returns_202_and_result_for_owner(monkeypatch):
    monkeypatch.setattr("shop.tasks.time.sleep", lambda _seconds: None)
    cache.clear()

    user = UserFactory()
    customer = CustomerFactory(user=user)

    order_one = OrderFactory(
        customer=customer,
        status=Order.Status.PAID,
    )

    order_two = OrderFactory(
        customer=customer,
        status=Order.Status.PENDING,
    )

    OrderItemFactory(
        order=order_one,
        quantity=2,
        unit_price=Decimal("10.00"),
    )

    OrderItemFactory(
        order=order_two,
        quantity=1,
        unit_price=Decimal("5.50"),
    )

    # Esta encomenda pertence a outra pessoa e não deve entrar no relatório.
    OrderFactory()

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        "/api/v1/reports/orders/",
        {},
        format="json",
    )

    assert response.status_code == 202
    assert response["Location"] == response.data["status_url"]
    assert response.data["id"]

    status_response = client.get(response.data["status_url"])

    assert status_response.status_code == 200
    assert status_response.data["state"] == "SUCCESS"
    assert status_response.data["result"]["orders"] == 2
    assert status_response.data["result"]["amount"] == "25.50"
    assert status_response.data["result"]["by_status"][Order.Status.PAID] == 1
    assert status_response.data["result"]["by_status"][Order.Status.PENDING] == 1
    assert status_response.data["error"] is None


@pytest.mark.django_db
def test_user_cannot_read_another_users_task_status(monkeypatch):
    monkeypatch.setattr("shop.tasks.time.sleep", lambda _seconds: None)
    cache.clear()

    owner = UserFactory()
    owner_customer = CustomerFactory(user=owner)
    owner_order = OrderFactory(customer=owner_customer)

    OrderItemFactory(order=owner_order)

    owner_client = APIClient()
    owner_client.force_authenticate(user=owner)

    created = owner_client.post(
        "/api/v1/reports/orders/",
        {},
        format="json",
    )

    assert created.status_code == 202

    other_user = UserFactory()

    other_client = APIClient()
    other_client.force_authenticate(user=other_user)

    forbidden = other_client.get(created.data["status_url"])

    assert forbidden.status_code == 404


@pytest.mark.django_db
def test_manager_can_read_another_users_task_status(monkeypatch):
    monkeypatch.setattr("shop.tasks.time.sleep", lambda _seconds: None)
    cache.clear()

    owner = UserFactory()
    customer = CustomerFactory(user=owner)
    order = OrderFactory(customer=customer)

    OrderItemFactory(order=order)

    owner_client = APIClient()
    owner_client.force_authenticate(user=owner)

    created = owner_client.post(
        "/api/v1/reports/orders/",
        {},
        format="json",
    )

    assert created.status_code == 202

    manager = UserFactory()

    managers_group, _created = Group.objects.get_or_create(
        name="gestores",
    )

    manager.groups.add(managers_group)

    manager_client = APIClient()
    manager_client.force_authenticate(user=manager)

    response = manager_client.get(created.data["status_url"])

    assert response.status_code == 200
    assert response.data["state"] == "SUCCESS"


@pytest.mark.django_db
def test_manager_report_includes_all_customers_orders(monkeypatch):
    monkeypatch.setattr("shop.tasks.time.sleep", lambda _seconds: None)
    cache.clear()

    customer_one = CustomerFactory()
    customer_two = CustomerFactory()

    order_one = OrderFactory(customer=customer_one)
    order_two = OrderFactory(customer=customer_two)

    OrderItemFactory(
        order=order_one,
        quantity=1,
        unit_price=Decimal("10.00"),
    )

    OrderItemFactory(
        order=order_two,
        quantity=2,
        unit_price=Decimal("7.50"),
    )

    manager = UserFactory()

    managers_group, _created = Group.objects.get_or_create(
        name="gestores",
    )

    manager.groups.add(managers_group)

    client = APIClient()
    client.force_authenticate(user=manager)

    created = client.post(
        "/api/v1/reports/orders/",
        {},
        format="json",
    )

    assert created.status_code == 202

    status_response = client.get(created.data["status_url"])

    assert status_response.status_code == 200
    assert status_response.data["result"]["orders"] == 2
    assert status_response.data["result"]["amount"] == "25.00"


@pytest.mark.django_db
def test_report_task_updates_progress_for_each_order(monkeypatch):
    monkeypatch.setattr("shop.tasks.time.sleep", lambda _seconds: None)

    updates = []

    monkeypatch.setattr(
        export_orders_report,
        "update_state",
        lambda **kwargs: updates.append(kwargs),
    )

    customer = CustomerFactory()

    order_one = OrderFactory(customer=customer)
    order_two = OrderFactory(customer=customer)

    OrderItemFactory(order=order_one)
    OrderItemFactory(order=order_two)

    result = export_orders_report.run(
        customer.user_id,
        customer.pk,
    )

    assert result["orders"] == 2

    assert updates == [
        {
            "state": "PROGRESS",
            "meta": {
                "current": 1,
                "total": 2,
            },
        },
        {
            "state": "PROGRESS",
            "meta": {
                "current": 2,
                "total": 2,
            },
        },
    ]


@pytest.mark.django_db
def test_unknown_task_status_returns_404():
    user = UserFactory()

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get(
        "/api/v1/tasks/nonexistent-task-id/",
    )

    assert response.status_code == 404