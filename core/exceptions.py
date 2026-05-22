# core/exceptions.py
import logging
from typing import Any, Dict, Optional

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger(__name__)


def _base_payload(
    *,
    code: str,
    message: str,
    status_code: int,
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Normalised error envelope for all responses.
    """
    payload: Dict[str, Any] = {
        "code": code,  # machine-friendly error code
        "message": message,  # human-readable summary
    }
    if details:
        payload["details"] = details  # field-level or extra context
    return payload


def exception_handler(exc: Exception, context: Dict[str, Any]) -> Response:
    """
    DRF-compatible exception handler that:
      - Produces a consistent JSON body: {code, message, details?}
      - Maps common Django/DRF errors to stable status codes
      - Falls back to DRF's default for anything we don't recognise
    """
    # First, let DRF translate known exceptions to a Response (status + data)
    response = drf_exception_handler(exc, context)

    # 1) Known DRF exceptions that DRF already turned into a Response
    if response is not None:
        code = getattr(exc, "default_code", exc.__class__.__name__.lower())
        message = getattr(exc, "detail", response.data)
        # ValidationError.detail is often a dict/list → move under "details"
        details = None
        if isinstance(exc, exceptions.ValidationError):
            # Let "message" be a short summary; push field errors into details
            message = "Validation failed."
            details = response.data
        elif isinstance(response.data, dict) and "detail" in response.data:
            # Common DRF shape; keep the human string in message
            message = response.data.get("detail") or str(exc)

        payload = _base_payload(
            code=str(code),
            message=str(message),
            status_code=response.status_code,
            details=details,
        )
        response.data = payload
        return response

    # 2) Map a few common Django exceptions not handled by DRF:
    if isinstance(exc, ObjectDoesNotExist):
        payload = _base_payload(
            code="not_found",
            message="The requested resource was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )
        return Response(payload, status=status.HTTP_404_NOT_FOUND)

    if isinstance(exc, IntegrityError):
        payload = _base_payload(
            code="conflict",
            message="A conflicting record already exists.",
            status_code=status.HTTP_409_CONFLICT,
        )
        return Response(payload, status=status.HTTP_409_CONFLICT)

    # 3) Fallback: unexpected error → generic 500 without internals
    payload = _base_payload(
        code="server_error",
        message="An unexpected error occurred.",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
    logger.exception("Unhandled exception in exception_handler: %s", exc)
    return Response(payload, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
