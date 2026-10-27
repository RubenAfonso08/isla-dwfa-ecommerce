from decimal import Decimal

from django.db import transaction
from django.db.models import DecimalField, ExpressionWrapper, F, Sum
from rest_framework.exceptions import APIException

from .models import Order, OrderItem, Payment


class OrderPaymentConflict(APIException):
    status_code = 409
    default_detail = "A encomenda não pode ser paga no estado atual."
    default_code = "order_payment_conflict"


@transaction.atomic
def pay_order(order):
    """
    Paga uma encomenda pendente e atualiza o respetivo pagamento.

    Toda a operação ocorre numa transação para evitar atualizações
    parciais da encomenda e do pagamento.
    """
    order = Order.objects.select_for_update().get(pk=order.pk)

    if order.status != Order.Status.PENDING:
        raise OrderPaymentConflict("Só é possível pagar encomendas pendentes.")

    line_total = ExpressionWrapper(
        F("quantity") * F("unit_price"),
        output_field=DecimalField(max_digits=12, decimal_places=2),
    )

    total = OrderItem.objects.filter(order=order).aggregate(total=Sum(line_total))[
        "total"
    ] or Decimal("0.00")

    if total <= Decimal("0.00"):
        raise OrderPaymentConflict("Não é possível pagar uma encomenda sem artigos.")

    payment, created = Payment.objects.get_or_create(
        order=order,
        defaults={
            "amount": total,
            "status": Payment.Status.PENDING,
            "provider": "demo",
        },
    )

    if not created:
        payment = Payment.objects.select_for_update().get(pk=payment.pk)

    if payment.status != Payment.Status.PENDING:
        raise OrderPaymentConflict("O pagamento não está pendente.")

    payment.amount = total
    payment.status = Payment.Status.COMPLETED
    payment.save(update_fields=["amount", "status"])

    order.status = Order.Status.PAID
    order.save(update_fields=["status", "updated_at"])

    return order
