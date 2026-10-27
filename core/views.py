from django.db import OperationalError, connection
from django.http import JsonResponse


def health(request):
    """GET /api/health/ — 200 if the app can talk to PostgreSQL, 503 otherwise.

    PT: a vista decide o código de estado — se a base de dados não responde, a
    aplicação não está "saudável": 503 Service Unavailable, nunca 500/traceback.
    EN: the view decides the status code — when the database does not answer,
    the app is not healthy: 503 Service Unavailable, never a 500/traceback.
    """
    try:
        with connection.cursor() as cur:
            cur.execute("SELECT 1")
    except OperationalError:
        return JsonResponse({"status": "degraded", "db": "unavailable"}, status=503)
    return JsonResponse({"status": "ok", "db": "ok"})
