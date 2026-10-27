from rest_framework.permissions import SAFE_METHODS, BasePermission


def is_gestor(user):
    """Verifica se o utilizador pertence ao grupo gestores."""
    return user.is_authenticated and user.groups.filter(name="gestores").exists()


class IsGestor(BasePermission):
    """Permite acesso apenas a gestores."""

    def has_permission(self, request, view):
        return is_gestor(request.user)


class IsGestorOrReadOnly(BasePermission):
    """Permite leituras públicas e escrita apenas a gestores."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return is_gestor(request.user)


class IsOwnerOrGestor(BasePermission):
    """Permite acesso à encomenda ao seu dono ou a um gestor."""

    def has_object_permission(self, request, view, obj):
        return is_gestor(request.user) or obj.customer.user_id == request.user.id
