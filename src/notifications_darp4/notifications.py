"""
Funciones de alto nivel para encolar notificaciones via Google Cloud Tasks.

Cada función construye la URL del endpoint correspondiente de la API
de notificaciones y encola un task HTTP con el payload adecuado.

#### Variables de entorno requeridas:
    NOTIFICATION_SERVICE_URL: URL base del servicio (ej: https://darp4-service-xxx.run.app)
    NOTIFICATION_QUEUE_NAME: Nombre de la cola (default: notification-queue)
"""

from gcp_darp4.cloud_tasks import enqueue_task
from datetime import datetime
import os
import logging


logger = logging.getLogger(__name__)

NOTIFICATION_SERVICE_URL = os.getenv("NOTIFICATION_SERVICE_URL", "")
NOTIFICATION_QUEUE_NAME = os.getenv("NOTIFICATION_QUEUE_NAME", "notification-queue")


def _build_url(path: str) -> str:
    """Construye la URL completa del endpoint de notificaciones."""
    base = NOTIFICATION_SERVICE_URL.rstrip("/")
    return f"{base}/notifications{path}"


def enqueue_notification_to_user(
    user_id: str,
    title: str,
    body: str,
    notif_type: str = "info",
    data: dict | None = None,
    schedule_time: datetime | None = None,
) -> str:
    """
    Encola una notificación para un usuario específico.

    Crea un task que invoca POST /notifications/send/{user_id}
    con el payload de la notificación.

    #### Args:
        user_id: str -> ID del usuario destinatario.
        title: str -> Título de la notificación.
        body: str -> Cuerpo de la notificación.
        notif_type: str -> Tipo de notificación (default: "info").
        data: dict | None -> Datos adicionales (default: {}).
        schedule_time: datetime | None -> Ejecución diferida (opcional).

    #### Returns:
        str: Nombre del task creado en Cloud Tasks.
    """
    url = _build_url(f"/send/{user_id}")
    payload = {
        "title": title,
        "body": body,
        "type": notif_type,
        "data": data or {},
    }

    logger.info(f"Enqueuing notification to user {user_id}: {title}")

    return enqueue_task(
        queue_name=NOTIFICATION_QUEUE_NAME,
        url=url,
        payload=payload,
        schedule_time=schedule_time,
    )


def enqueue_notification_bulk(
    user_ids: list[str],
    title: str,
    body: str,
    notif_type: str = "info",
    data: dict | None = None,
    schedule_time: datetime | None = None,
) -> str:
    """
    Encola una notificación masiva para una lista de usuarios.

    Crea un task que invoca POST /notifications/send_bulk
    con los IDs de los usuarios y el payload.

    #### Args:
        user_ids: list[str] -> Lista de IDs de usuarios destinatarios.
        title: str -> Título de la notificación.
        body: str -> Cuerpo de la notificación.
        notif_type: str -> Tipo de notificación (default: "info").
        data: dict | None -> Datos adicionales (default: {}).
        schedule_time: datetime | None -> Ejecución diferida (opcional).

    #### Returns:
        str: Nombre del task creado en Cloud Tasks.
    """
    url = _build_url("/send_bulk")
    payload = {
        "user_ids": user_ids,
        "title": title,
        "body": body,
        "type": notif_type,
        "data": data or {},
    }

    logger.info(f"Enqueuing bulk notification to {len(user_ids)} users: {title}")

    return enqueue_task(
        queue_name=NOTIFICATION_QUEUE_NAME,
        url=url,
        payload=payload,
        schedule_time=schedule_time,
    )


def enqueue_notification_by_tenant(
    tenant_id: str,
    title: str,
    body: str,
    notif_type: str = "info",
    data: dict | None = None,
    schedule_time: datetime | None = None,
) -> str:
    """
    Encola una notificación para todos los usuarios de un tenant.

    Crea un task que invoca POST /notifications/send_by_tenant/{tenant_id}
    con el payload de la notificación.

    #### Args:
        tenant_id: str -> ID del tenant.
        title: str -> Título de la notificación.
        body: str -> Cuerpo de la notificación.
        notif_type: str -> Tipo de notificación (default: "info").
        data: dict | None -> Datos adicionales (default: {}).
        schedule_time: datetime | None -> Ejecución diferida (opcional).

    #### Returns:
        str: Nombre del task creado en Cloud Tasks.
    """
    url = _build_url(f"/send_by_tenant/{tenant_id}")
    payload = {
        "title": title,
        "body": body,
        "type": notif_type,
        "data": data or {},
    }

    logger.info(f"Enqueuing notification to tenant {tenant_id}: {title}")

    return enqueue_task(
        queue_name=NOTIFICATION_QUEUE_NAME,
        url=url,
        payload=payload,
        schedule_time=schedule_time,
    )


def enqueue_notification_by_role(
    tenant_id: str,
    role_name: str,
    title: str,
    body: str,
    notif_type: str = "info",
    data: dict | None = None,
    schedule_time: datetime | None = None,
) -> str:
    """
    Encola una notificación para todos los usuarios con un rol
    específico dentro de un tenant.

    Crea un task que invoca
    POST /notifications/send_by_role/{tenant_id}/role/{role_name}
    con el payload de la notificación.

    #### Args:
        tenant_id: str -> ID del tenant.
        role_name: str -> Nombre del rol (ej: "admin", "driver").
        title: str -> Título de la notificación.
        body: str -> Cuerpo de la notificación.
        notif_type: str -> Tipo de notificación (default: "info").
        data: dict | None -> Datos adicionales (default: {}).
        schedule_time: datetime | None -> Ejecución diferida (opcional).

    #### Returns:
        str: Nombre del task creado en Cloud Tasks.
    """
    url = _build_url(f"/send_by_role/{tenant_id}/role/{role_name}")
    payload = {
        "title": title,
        "body": body,
        "type": notif_type,
        "data": data or {},
    }

    logger.info(
        f"Enqueuing notification to role '{role_name}' "
        f"of tenant {tenant_id}: {title}"
    )

    return enqueue_task(
        queue_name=NOTIFICATION_QUEUE_NAME,
        url=url,
        payload=payload,
        schedule_time=schedule_time,
    )
