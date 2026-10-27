"""Desenvolvimento local · local development."""

from .base import *  # noqa: F403
from .base import env

DEBUG = env("DEBUG", default=True)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

# Email para a consola em dev · email to the console in dev
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
