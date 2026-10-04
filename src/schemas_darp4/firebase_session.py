from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime
from typing import Any


class FirebaseInfoSchema(BaseModel):
    """Información del proveedor de identidad de Firebase.
        sign_in_provider: Proveedor utilizado para autenticarse (p.ej. 'password', 'google.com', 'anonymous').
        identities: Mapa de identidades vinculadas al usuario por proveedor.
    """
    sign_in_provider: str
    identities: dict[str, Any] = {}


class FirebaseSessionSchema(BaseModel):
    """Esquema de datos que representa el payload de un ID Token de Firebase Auth después de ser validado.

        sub:             Identificador único del usuario (uid) en Firebase.
        iss:             Emisor del token (https://securetoken.google.com/<project_id>).
        aud:             Audiencia del token (project_id de Firebase).
        iat:             Fecha y hora de emisión del token.
        exp:             Fecha y hora de expiración del token.
        auth_time:       Fecha y hora en que el usuario se autenticó por última vez.
        uid:             Alias de sub; identificador único del usuario en Firebase.
        email:           Dirección de correo electrónico del usuario (opcional).
        email_verified:  Indica si el correo electrónico del usuario ha sido verificado.
        name:            Nombre de pila del usuario (opcional).
        picture:         URL de la foto de perfil del usuario (opcional).
        firebase:        Metadatos específicos de Firebase (proveedor de identidad, etc.).

        Custom claims:   Cualquier campo adicional definido vía Firebase Admin SDK
                         (p.ej. role, plan, tenant_id) estará disponible directamente
                         como atributo del modelo gracias a extra='allow'.
    """
    model_config = ConfigDict(extra="allow")

    sub: str
    iss: str
    aud: str
    iat: datetime
    exp: datetime
    auth_time: datetime
    uid: str
    email: EmailStr | None = None
    email_verified: bool = False
    name: str | None = None
    picture: str | None = None
    firebase: FirebaseInfoSchema
