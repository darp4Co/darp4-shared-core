from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
import os

CF_SECRET = os.getenv("CLOUDFLARE_SECRET_KEY", "")

class CloudflareOriginMiddleware(BaseHTTPMiddleware):
    """
    Middleware para proteger el servicio de Cloud Run de accesos directos.
    Solo permite peticiones que vengan desde Cloudflare.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # 1. Allow local traffic so you can continue testing on your own machine
        if request.client.host == "127.0.0.1" or request.url.hostname in ["localhost", "127.0.0.1"]:
            return await call_next(request)
        
        # 2. Check for the Cloudflare secret stamp
        incoming_secret = request.headers.get("X-Darp4-CF-Key")
        
        if incoming_secret != CF_SECRET:
            # Reject direct attacks hitting the Google Cloud Run URL immediately
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "Direct access forbidden. Traffic must route through the official API domain."}
            )
            
        # 3. If the password matches, process the request normally
        return await call_next(request)