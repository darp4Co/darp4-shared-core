from pydantic import BaseModel
from datetime import datetime

class SessionSchema(BaseModel):
    """Esquema de datos que representa la información contenida en el payload de un token JWT después de ser validado.
    - sub: Identificador del sujeto (usuario) al que pertenece el token.
    - iat: Fecha y hora de emisión del token.
    - exp: Fecha y hora de expiración del token.
    - iss: Emisor del token.
    - aud: Audiencia del token.
    - tenant: Identificador del tenant al que pertenece el usuario.
    - campus: Identificador del campus al que pertenece el usuario.
    """
    sub: str
    iat: datetime
    exp: datetime
    iss: str
    aud: str
    tenant: str
    campus: str
