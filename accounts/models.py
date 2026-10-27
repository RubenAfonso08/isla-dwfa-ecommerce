from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Modelo de utilizador do projeto · the project's user model.

    PT: vazio por agora, de propósito. Trocar o modelo de utilizador *depois* da
    primeira migração é doloroso; declará-lo no dia zero é grátis. Os outros
    modelos referem-no via `settings.AUTH_USER_MODEL`, nunca `User` diretamente.
    EN: empty on purpose. Swapping the user model *after* the first migration is
    painful; declaring it on day zero is free. Other models refer to it through
    `settings.AUTH_USER_MODEL`, never `User` directly.
    """

    class Meta(AbstractUser.Meta):
        db_table = "accounts_user"
