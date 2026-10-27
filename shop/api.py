from rest_framework.views import exception_handler


def problem_details_handler(exc, context):
    response = exception_handler(exc, context)

    # Se não for uma exceção tratada pelo DRF, mantém o erro original.
    if response is None:
        return None

    detail = response.data

    response.data = {
        "type": "about:blank",
        "title": response.status_text,
        "status": response.status_code,
        "errors": (detail if isinstance(detail, dict) else {"detail": detail}),
    }

    response.content_type = "application/problem+json"

    return response
