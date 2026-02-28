import uuid
import logging
from fastapi import Request

logger = logging.getLogger("request")

async def request_context_middleware(request: Request, call_next):
    """
    Middleware para agregar un request_id a cada request.

    #### Args:
        request: Request -> Request FastAPI.
        call_next: Callable -> Función a la que se le pasa el request.

    #### Returns:
        Response: Response FastAPI.
    """
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

    response = None
    try:
        response = await call_next(request)
        return response
    finally:
        logger.info(
            "request_completed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": getattr(response, "status_code", None),
            },
        )
