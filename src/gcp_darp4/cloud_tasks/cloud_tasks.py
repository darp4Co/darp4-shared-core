"""
Módulo genérico para encolar tareas HTTP en Google Cloud Tasks.

Proporciona una función `enqueue_task` reutilizable que crea tasks HTTP
con autenticación OIDC para invocar endpoints de Cloud Run.

En entorno local (ENVIRONMENT=local) hace una llamada HTTP directa
usando httpx en lugar de encolar en Cloud Tasks.
"""

from google.cloud import tasks_v2
from google.protobuf import timestamp_pb2
from datetime import datetime, timezone
import json
import os
import logging
import httpx


logger = logging.getLogger(__name__)

ENVIRONMENT = os.getenv("ENVIRONMENT", "local")
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "darp4-dev")
GCP_LOCATION = os.getenv("GCP_LOCATION", "us-central1")
GCP_SERVICE_ACCOUNT_EMAIL = os.getenv("GCP_SERVICE_ACCOUNT_EMAIL", "")


def enqueue_task(
    queue_name: str,
    url: str,
    payload: dict,
    http_method: str = "POST",
    schedule_time: datetime | None = None,
) -> str:
    """
    Encola un task HTTP en Google Cloud Tasks.

    En entorno local, ejecuta la llamada HTTP directamente con httpx
    en lugar de usar la cola de Cloud Tasks.

    #### Args:
        queue_name: str -> Nombre de la cola de Cloud Tasks.
        url: str -> URL completa del endpoint HTTP a invocar.
        payload: dict -> Cuerpo del request (se serializa a JSON).
        http_method: str -> Método HTTP (default: POST).
        schedule_time: datetime | None -> Tiempo de ejecución programado (opcional).

    #### Returns:
        str: Nombre del task creado, o "local-direct-call" en entorno local.

    #### Raises:
        Exception: Si ocurre un error al crear el task o al hacer la llamada.
    """
    if ENVIRONMENT == "local":
        return _execute_local(url, payload, http_method)

    return _enqueue_cloud_task(queue_name, url, payload, http_method, schedule_time)


def _execute_local(url: str, payload: dict, http_method: str) -> str:
    """
    Fallback local: ejecuta la llamada HTTP directamente.
    """
    try:
        logger.info(f"[Cloud Tasks LOCAL] {http_method} {url}")

        method_fn = getattr(httpx, http_method.lower(), httpx.post)
        response = method_fn(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30.0,
        )
        logger.info(f"[Cloud Tasks LOCAL] Response: {response.status_code}")
        return "local-direct-call"
    except Exception as e:
        logger.error(f"[Cloud Tasks LOCAL] Error: {e}")
        raise


def _enqueue_cloud_task(
    queue_name: str,
    url: str,
    payload: dict,
    http_method: str,
    schedule_time: datetime | None,
) -> str:
    """
    Encola el task en Google Cloud Tasks con autenticación OIDC.
    """
    client = tasks_v2.CloudTasksClient()

    parent = client.queue_path(GCP_PROJECT_ID, GCP_LOCATION, queue_name)

    http_method_enum = tasks_v2.HttpMethod[http_method.upper()]

    body = json.dumps(payload).encode("utf-8")

    http_request = tasks_v2.HttpRequest(
        http_method=http_method_enum,
        url=url,
        headers={"Content-Type": "application/json"},
        body=body,
    )

    # Autenticación OIDC para Cloud Run
    if GCP_SERVICE_ACCOUNT_EMAIL:
        http_request.oidc_token = tasks_v2.OidcToken(
            service_account_email=GCP_SERVICE_ACCOUNT_EMAIL,
            audience=url,
        )

    task = tasks_v2.Task(http_request=http_request)

    # Programar ejecución diferida si se especifica
    if schedule_time:
        timestamp = timestamp_pb2.Timestamp()
        timestamp.FromDatetime(schedule_time.astimezone(timezone.utc))
        task.schedule_time = timestamp

    response = client.create_task(
        tasks_v2.CreateTaskRequest(parent=parent, task=task)
    )

    logger.info(f"[Cloud Tasks] Task created: {response.name}")
    return response.name
