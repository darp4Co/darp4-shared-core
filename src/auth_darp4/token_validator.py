from jwt import (
    PyJWKClient,
    decode
)
from logging import getLogger
from traceback import format_exc
from typing import Any
from schemas_darp4 import SessionSchema

logger = getLogger("uvicorn.error")

class TokenValidator:
    
    """
    Clase encargada de obtener el Json Web Key Set (JWKS) y validar los tokens JWT utilizando la biblioteca PyJWT.
     - jwks_url: URL del JWKS para obtener las claves públicas.
     - issuer: Emisor esperado del token JWT.
     - audience: Audiencia esperada del token JWT.
     
     uso recomendado:
    
        token_validator = TokenValidator(
            jwks_url="https://example.com/.well-known/jwks.json",
            issuer="https://example.com/",
            audience="my-audience"
        ) # Crea una instancia del validador de tokens con la configuración adecuada

        app.state.token_validator = token_validator # Almacena el validador en el estado de la aplicación para su uso posterior
        
        session_data = await app.state.token_validator.validate(token="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...")

        opcional:
            crea una dependencia para obtener el usuario autenticado a partir del token JWT en las rutas de FastAPI, utilizando el validador de tokens almacenado en el estado de la aplicación.
            
            cookie_schema = ApiKeyCookie(name="access_token", auto_error=True) # Define un esquema de cookie para extraer el token JWT de las cookies de la solicitud

            def get_current_user(request: Request, token: Depends(cookie_schema)) -> SessionSchema:
                
                token_validator: TokenValidator = request.app.state.token_validator # Obtiene el validador de tokens del estado de la aplicación
                
                return await token_validator.validate(token=token) # Valida el token JWT y retorna los datos de la sesión si es válido
    """

    __slots__ = ("jwks_client", "issuer", "audience")

    def __init__(
            self,
            jwks_url: str,
            issuer: str,
            audience: str
    ):
        self.jwks_client: PyJWKClient = PyJWKClient(
            uri=jwks_url,
            cache_keys=True
        )
        self.issuer: str = issuer
        self.audience: str = audience
    
    async def validate(self, token:str) -> SessionSchema:
        """
        Valida un token JWT utilizando la clave obtenida del JWKS y decodifica su payload.
            - token: Token JWT a validar.
            Retorna un objeto SessionSchema con los datos del payload si la validación es exitosa.
            lanza una excepción si la validación falla o si ocurre algún error durante el proceso.
        """
        try:

            signing_key = self.jwks_client.get_signing_key_from_jwt(token=token)

            payload: dict[str, Any] = decode(
                jwt=token,
                key=signing_key,
                algorithms=["RS256"],
                audience=self.audience,
                issuer=self.issuer
            )

            return SessionSchema(**payload)
        
        except Exception as e:
            logger.error(f"error al validar JWT token e: {e}, traceback: {format_exc()}")
            raise