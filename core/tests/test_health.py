from unittest.mock import patch

import pytest
from django.db import OperationalError


@pytest.mark.django_db
def test_health_ok_when_db_answers(client):
    r = client.get("/api/health/")
    assert r.status_code == 200
    assert r["Content-Type"] == "application/json"
    assert r.json() == {"status": "ok", "db": "ok"}


def test_health_503_when_db_is_down(client):
    # PT: simula a base de dados em baixo sem a parar · EN: simulate the DB down without stopping it
    with patch("core.views.connection.cursor", side_effect=OperationalError("db down")):
        r = client.get("/api/health/")
    assert r.status_code == 503
    assert r.json()["db"] == "unavailable"
