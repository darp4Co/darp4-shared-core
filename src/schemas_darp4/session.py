from pydantic import BaseModel
from datetime import datetime

class SessionSchema(BaseModel):
    """Esquema de datos que representa la información contenida en el payload de un token JWT después de ser validado.
        sub: Identificador del sujeto (usuario) al que pertenece el token.
        tid: Tenant id
        tcd: Tenant code
        sid: Session id
        iat: Fecha y hora de emisión del token.
        exp: Fecha y hora de expiración del token.
        iss: Emisor del token.
        aud: Audience del token.
        jti: Token id
        role: Información del rol del usuario.
        campus: Información del campus del usuario.
    """
    sub: str
    tid: str
    tcd: str
    sid: str
    iss: str
    aud: str
    iat: datetime
    exp: datetime
    jti: str
    role: RoleSessionSchema
    campus: CampusSessionSchema

class CampusSessionSchema(BaseModel):
    id: int
    name: str

class RoleSessionSchema(BaseModel):
    id: int
    name: str
    