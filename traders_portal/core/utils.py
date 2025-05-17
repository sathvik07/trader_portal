from django_ratelimit.exceptions import Ratelimited
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    # Handle rate limit explicitly
    if isinstance(exc, Ratelimited):
        return Response(
            {'detail': 'Rate limit exceeded. Try again in a moment.'},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )

    # Call DRF's default exception handler
    response = exception_handler(exc, context)

    # Enhance response if it exists
    if response is not None:
        view = context.get('view', None)
        logger.warning(f"{type(exc).__name__} in {view}: {str(exc)}")
        response.data['status_code'] = response.status_code
        response.data['error_type'] = type(exc).__name__
        if isinstance(exc, (ValidationError, NotFound, PermissionDenied)):
            response.data['detail'] = str(exc.detail)
        else:
            response.data['detail'] = str(exc)
        return response

    # For unhandled exceptions
    logger.error(f"Unhandled exception: {type(exc).__name__} - {str(exc)}")
    return Response({
        'error_type': type(exc).__name__,
        'detail': str(exc),
        'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
