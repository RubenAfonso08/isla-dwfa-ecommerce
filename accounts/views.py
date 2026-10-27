from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView


class ThrottledTokenObtainPairView(TokenObtainPairView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "username": {"type": "string"},
                    "groups": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
                "required": ["id", "username", "groups"],
            },
        },
        summary="Obter o utilizador autenticado",
        description=(
            "Devolve o identificador, o nome de utilizador e os grupos do utilizador autenticado."
        ),
    )
    def get(self, request):
        user = request.user

        return Response(
            {
                "id": user.pk,
                "username": user.get_username(),
                "groups": list(user.groups.values_list("name", flat=True)),
            }
        )
