import pytest
from django.conf import settings
from django.contrib.auth import get_user_model

from accounts.factories import UserFactory


def test_custom_user_model_is_configured():
    assert settings.AUTH_USER_MODEL == "accounts.User"
    assert get_user_model()._meta.label == "accounts.User"


@pytest.mark.django_db
def test_user_factory_builds_a_user_that_can_log_in(client):
    user = UserFactory()
    assert client.login(username=user.username, password="pass1234")
