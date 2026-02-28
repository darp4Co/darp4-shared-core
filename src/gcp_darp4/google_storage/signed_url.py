from google.cloud import storage
from google.auth import default, impersonated_credentials
from datetime import timedelta
import os

ENVIRONMENT = os.getenv("ENVIRONMENT", "local")

BUCKET_NAME = os.getenv("BUCKET_NAME", "darp4-storage")
TARGET_SA = os.getenv("TARGET_SA", "979750909530-compute@developer.gserviceaccount.com")


async def generate_signed_url(path: str, method: str = "GET", expiration: int = 60, content_type: str | None = None) -> str:
    """
    Genera un URL firmado para acceder a un objeto en Google Storage.

    #### Args:
        path: str -> Ruta del objeto en Google Storage.
        method: str -> Método HTTP para el URL (GET, POST, PUT, DELETE).
        expiration: int -> Duración del URL en minutos.
        content_type: str | None -> Tipo de contenido del objeto.

    #### Returns:
        str: URL firmado.

    #### Raises:
        Exception: Si ocurre un error al generar el URL firmado.
    """
    if ENVIRONMENT == "local":
        client = storage.Client.from_service_account_json(
            "service_account.json"
        )
    else:
        source_credentials, _ = default()

        credentials = impersonated_credentials.Credentials(
            source_credentials=source_credentials,
            target_principal=TARGET_SA,
            target_scopes=["https://www.googleapis.com/auth/cloud-platform"],
            lifetime=3600,
        )

        client = storage.Client(credentials=credentials)

    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(path)

    url_params = {
        "expiration": timedelta(minutes=expiration),
        "method": method,
    }

    if content_type:
        url_params["content_type"] = content_type

    url = blob.generate_signed_url(**url_params)

    return url
