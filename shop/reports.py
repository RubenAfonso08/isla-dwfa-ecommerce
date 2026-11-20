import uuid

from celery.result import AsyncResult
from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Customer
from .permissions import is_gestor
from .tasks import export_orders_report


class OrdersReportView(APIView):
    """Enfileira um relatório de encomendas e responde sem esperar pela tarefa."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        customer_id = None

        if not is_gestor(user):
            customer_id = (
                Customer.objects.filter(user=user)
                .values_list("pk", flat=True)
                .first()
            )

        task_id = str(uuid.uuid4())
        owner_key = f"task:{task_id}:owner"

        cache.set(owner_key, user.pk, timeout=3600)

        try:
            export_orders_report.apply_async(
                args=(user.pk, customer_id),
                task_id=task_id,
            )
        except Exception:
            cache.delete(owner_key)
            raise

        status_url = reverse("task-status", kwargs={"task_id": task_id})

        return Response(
            {
                "id": task_id,
                "status_url": status_url,
            },
            status=status.HTTP_202_ACCEPTED,
            headers={"Location": status_url},
        )


class TaskStatusView(APIView):
    """Devolve o estado de uma tarefa apenas ao seu dono ou a um gestor."""

    permission_classes = [IsAuthenticated]

    def get(self, request, task_id):
        owner_id = cache.get(f"task:{task_id}:owner")

        if owner_id is None:
            raise NotFound()

        if owner_id != request.user.pk and not is_gestor(request.user):
            raise NotFound()

        task = AsyncResult(task_id, app=export_orders_report.app)
        task_state = task.state
        task_info = task.info

        progress = None
        result = None
        error = None

        if task_state == "PROGRESS" and isinstance(task_info, dict):
            progress = task_info
        elif task_state == "SUCCESS":
            result = task.result
        elif task_state == "FAILURE":
            error = str(task_info)

        return Response(
            {
                "id": task_id,
                "state": task_state,
                "progress": progress,
                "result": result,
                "error": error,
            }
        )