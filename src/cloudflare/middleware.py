from fastapi import Request, status
from fastapi.responses import JSONResponse
import os


CF_SECRET = os.getenv("CLOUDFLARE_SECRET_KEY")

async def verify_cloudflare_origin(request: Request, call_next):
    # 1. Allow local traffic so you can continue testing on your own machine
    if request.client.host == "127.0.0.1" or request.url.hostname in ["localhost", "127.0.0.1"]:
        return await call_next(request)
        
    # 2. Check for the Cloudflare secret stamp
    incoming_secret = request.headers.get("X-CF-Secret-Key")
    
    if incoming_secret != CF_SECRET:
        # Reject direct attacks hitting the Google Cloud Run URL immediately
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": "Direct access forbidden. Traffic must route through the official API domain."}
        )
        
    # 3. If the password matches, process the request normally
    return await call_next(request)