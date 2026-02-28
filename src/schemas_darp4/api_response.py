from typing import Generic, Optional, TypeVar
from datetime import datetime, timezone
from sqlmodel import SQLModel


T = TypeVar("T")

class ErrorSchema(SQLModel):
    """
    Esquema para el error de la respuesta.

    #### Args:
        code: str -> Código del error.
        message: str -> Mensaje del error.

    #### Returns:
        ErrorSchema: Esquema para el error de la respuesta.
    """
    code: str
    message: str


class MetaSchema(SQLModel):
    timestamp: datetime = datetime.now(timezone.utc)


class ApiResponse(SQLModel, Generic[T]):
    """
    Respuesta estandarizada para las API.

    #### Args:
        ok: bool -> Indica si la respuesta es exitosa.
        data: Optional[T] -> Datos de la respuesta.
        error: Optional[ErrorSchema] -> Error de la respuesta.
        meta: MetaSchema -> Metadatos de la respuesta.

    #### Returns:
        ApiResponse: Respuesta estandarizada para las API.
    """
    ok: bool
    data: Optional[T] = None
    error: Optional[ErrorSchema] = None
    meta: MetaSchema = MetaSchema()
