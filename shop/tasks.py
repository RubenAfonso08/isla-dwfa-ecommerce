import time
from decimal import Decimal

from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import DecimalField, ExpressionWrapper, F, Sum
from django.utils import timezone

from .models import Order, Payment
from .permissions import is_gestor


@shared_task(
    autoretry_for=(OSError,),
    retry_backoff=True,
    max_retries=3,
)
def send_order_receipt(order_id):
    """Envia o recibo de uma encomenda paga, sem enviar duplicados em execuções normais."""
    with transaction.atomic():
        payment = (
            Payment.objects.select_for_update(of=("self",))
            .select_related("order__customer__user")
            .get(order_id=order_id)
        )

        if payment.receipt_sent_at is not None:
            return "already-sent"

        if payment.status != Payment.Status.COMPLETED:
            return "not-paid"

        order = payment.order
        recipient = order.customer.user.email
        if not recipient:
            raise OSError("O cliente não tem um endereço de email definido.")

        sent = send_mail(
            subject=f"Recibo da encomenda {order.reference}",
            message=(
                f"Obrigado pela compra.\n"
                f"Encomenda: {order.reference}\n"
                f"Total pago: {payment.amount} EUR."
            ),
            from_email=None,
            recipient_list=[recipient],
        )

        if sent != 1:
            raise OSError("O backend de email não confirmou o envio do recibo.")

        payment.receipt_sent_at = timezone.now()
        payment.save(update_fields=["receipt_sent_at"])

    return "sent"


@shared_task(bind=True)
def export_orders_report(self, user_id, customer_id):
    """Gera um resumo das encomendas do cliente ou de todas as encomendas para gestores."""
    user_model = get_user_model()
    user = user_model.objects.filter(pk=user_id).first()
    if user is None:
        raise ValueError("O utilizador que pediu o relatório já não existe.")

    orders = Order.objects.all()

    if not is_gestor(user):
        if customer_id is None:
            orders = orders.none()
        else:
            orders = orders.filter(customer_id=customer_id)

    line_total = ExpressionWrapper(
        F("items__quantity") * F("items__unit_price"),
        output_field=DecimalField(max_digits=14, decimal_places=2),
    )

    orders = orders.annotate(
        report_total=Sum(line_total),
    ).order_by("pk")

    total_orders = orders.count()
    total_amount = Decimal("0.00")
    by_status = {status: 0 for status, _label in Order.Status.choices}

    for current, order in enumerate(orders.iterator(), start=1):
        order_amount = order.report_total or Decimal("0.00")
        total_amount += order_amount
        by_status[order.status] = by_status.get(order.status, 0) + 1

        self.update_state(
            state="PROGRESS",
            meta={"current": current, "total": total_orders},
        )

        time.sleep(0.2)

    return {
        "orders": total_orders,
        "amount": f"{total_amount:.2f}",
        "by_status": by_status,
    }