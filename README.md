# Darp4 Shared Core

Librería de código compartido para los servicios de la plataforma **Darp4**. Contiene esquemas de respuesta API, utilidades de base de datos (PostgreSQL, Redis), envío de correos, logging, generación de URLs firmadas para Google Cloud Storage, encolado de tareas con Google Cloud Tasks, y funciones de notificación asíncronas.

## Requisitos

- **Python** >= 3.10

## Instalación

```bash
pip install git+https://github.com/darp4Co/darp4-shared-core.git
```

O con una version especifica:

```bash
pip install git+https://github.com/darp4Co/darp4-shared-core.git@version_name
```

## Estructura del Proyecto

```
darp4-shared-core/
├── pyproject.toml
├── README.md
├── src/
│   ├── schemas_darp4/     # Esquemas de respuesta API estandarizados
│   ├── logging_darp4/     # Middleware de logging para FastAPI
│   ├── gcp_darp4/         # Integración con Google Cloud Platform
│   │   ├── google_storage/# URLs firmadas para GCS
│   │   └── cloud_tasks/   # Encolado de tareas HTTP con Cloud Tasks
│   ├── notifications_darp4/ # Notificaciones vía Cloud Tasks queue
│   ├── email_darp4/       # Envío de correos y templates HTML
│   └── database_darp4/    # Conexión a PostgreSQL y Redis
└── test/
```

---

## Módulos

### `schemas_darp4` — Respuestas API estandarizadas

Esquemas basados en SQLModel para unificar el formato de respuestas en las APIs.

**Importar:**

```python
from schemas_darp4.api_response import ApiResponse, ErrorSchema, MetaSchema
```

**Clases:**


| Clase            | Descripción                                       |
| ---------------- | ------------------------------------------------- |
| `ErrorSchema`    | Modelo para errores: `code`, `message`            |
| `MetaSchema`     | Metadatos con `timestamp` (UTC)                   |
| `ApiResponse[T]` | Respuesta genérica: `ok`, `data`, `error`, `meta` |


**Ejemplo:**

```python
# Respuesta exitosa
response = ApiResponse(ok=True, data={"user_id": 1}, error=None)

# Respuesta con error
response = ApiResponse(
    ok=False,
    data=None,
    error=ErrorSchema(code="NOT_FOUND", message="Usuario no encontrado"),
)
```

---

### `logging_darp4` — Middleware de FastAPI

Middleware que añade un identificador de request y registra cada petición al finalizar.

**Importar:**

```python
from logging_darp4.middleware import request_context_middleware
```

**Uso en FastAPI:**

```python
from fastapi import FastAPI

app = FastAPI()
app.middleware("http")(request_context_middleware)
```

**Comportamiento:**

- Lee o genera `X-Request-ID` en cada request
- Al terminar, loguea: `request_id`, `method`, `path`, `status_code`

---

### `database_darp4` — PostgreSQL y Redis

#### Sesiones PostgreSQL (SQLAlchemy async)

Conexión asíncrona a PostgreSQL vía Cloud SQL o local.

**Importar:**

```python
from database_darp4.session import get_engine, get_session
```

**Uso como dependencia FastAPI:**

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

@app.get("/items")
async def get_items(session: AsyncSession = Depends(get_session)):
    ...
```

**Variables de entorno:**


| Variable                   | Descripción                     | Ejemplo                   |
| -------------------------- | ------------------------------- | ------------------------- |
| `DB_USER`                  | Usuario PostgreSQL              | `postgres`                |
| `DB_PASSWORD`              | Contraseña                      | `*`***                    |
| `DB_NAME`                  | Nombre de la base de datos      | `darp4_db`                |
| `INSTANCE_CONNECTION_NAME` | Conexión Cloud SQL (producción) | `project:region:instance` |
| `ENVIRONMENT`              | `local` o `cloud`               | `local`                   |


#### Cliente Redis

Cliente Redis asíncrono (singleton) con respuestas decodificadas a `str`.

**Importar:**

```python
from database_darp4.redis import get_redis, REDIS_PREFIX, CACHE_TTL_SHORT, CACHE_TTL_MEDIUM, CACHE_TTL_LONG
```

**Ejemplo:**

```python
redis = await get_redis()
await redis.set(f"{REDIS_PREFIX}user:123", "data", ex=CACHE_TTL_MEDIUM)
value = await redis.get(f"{REDIS_PREFIX}user:123")
```

**Variables de entorno:**


| Variable           | Descripción          | Default     |
| ------------------ | -------------------- | ----------- |
| `REDIS_HOST`       | Host de Redis        | `127.0.0.1` |
| `REDIS_PORT`       | Puerto               | `6379`      |
| `REDIS_DB`         | Índice de BD         | `0`         |
| `REDIS_PREFIX`     | Prefijo para claves  | `dev:`      |
| `CACHE_TTL_SHORT`  | TTL corto (segundos) | `60`        |
| `CACHE_TTL_MEDIUM` | TTL medio            | `300`       |
| `CACHE_TTL_LONG`   | TTL largo            | `86400`     |


> Los TTL incluyen jitter aleatorio para evitar thundering herd.

---

### `gcp_darp4.google_storage` — URLs firmadas

Generación de URLs firmadas para acceder a objetos en Google Cloud Storage.

**Importar:**

```python
from gcp_darp4.google_storage.signed_url import generate_signed_url
```

**Ejemplo:**

```python
url = await generate_signed_url(
    path="documents/archivo.pdf",
    method="GET",
    expiration=60,
    content_type="application/pdf"
)
```

**Parámetros:**


| Parámetro      | Tipo  | Default | Descripción                          |
| -------------- | ----- | ------- | ------------------------------------ |
| `path`         | `str` | —       | Ruta del objeto en el bucket         |
| `method`       | `str` | `"GET"` | Método HTTP (GET, POST, PUT, DELETE) |
| `expiration`   | `int` | `60`    | Duración del URL en minutos          |
| `content_type` | `str  | None`   | `None`                               |


**Variables de entorno:**


| Variable      | Descripción                                | Default         |
| ------------- | ------------------------------------------ | --------------- |
| `ENVIRONMENT` | `local` o `cloud`                          | `local`         |
| `BUCKET_NAME` | Nombre del bucket GCS                      | `darp4-storage` |
| `TARGET_SA`   | Service account para impersonation (cloud) | —               |


> En `local` se usa `service_account.json`; en `cloud` se usan credenciales impersonadas.

---

### `gcp_darp4.cloud_tasks` — Encolado de tareas HTTP

Cliente genérico para encolar tareas HTTP en Google Cloud Tasks con autenticación OIDC.

**Importar:**

```python
from gcp_darp4.cloud_tasks import enqueue_task
```

**Ejemplo:**

```python
from datetime import datetime, timedelta, timezone

# Encolar un task HTTP inmediato
task_name = enqueue_task(
    queue_name="notification-queue",
    url="https://mi-servicio.run.app/api/procesar",
    payload={"order_id": "ord-123"},
)

# Encolar con ejecución diferida (30 minutos)
task_name = enqueue_task(
    queue_name="notification-queue",
    url="https://mi-servicio.run.app/api/recordatorio",
    payload={"user_id": "usr-456"},
    schedule_time=datetime.now(timezone.utc) + timedelta(minutes=30),
)
```

**Parámetros:**


| Parámetro       | Tipo             | Default  | Descripción                              |
| --------------- | ---------------- | -------- | ---------------------------------------- |
| `queue_name`    | `str`            | —        | Nombre de la cola de Cloud Tasks         |
| `url`           | `str`            | —        | URL completa del endpoint HTTP a invocar |
| `payload`       | `dict`           | —        | Cuerpo del request (serializado a JSON)  |
| `http_method`   | `str`            | `"POST"` | Método HTTP                              |
| `schedule_time` | `datetime | None`| `None`   | Ejecución diferida (opcional)            |


**Variables de entorno:**


| Variable                    | Descripción                        | Default        |
| --------------------------- | ---------------------------------- | -------------- |
| `GCP_PROJECT_ID`            | ID del proyecto de Google Cloud    | `darp4-dev`    |
| `GCP_LOCATION`              | Región de la cola                  | `us-central1`  |
| `GCP_SERVICE_ACCOUNT_EMAIL` | Service account para token OIDC    | —              |
| `ENVIRONMENT`               | `local` o `cloud`                  | `local`        |


> En `local`, se ejecuta la llamada HTTP directamente con `httpx` en lugar de encolar en Cloud Tasks (no hay emulador disponible).

---

### `notifications_darp4` — Notificaciones vía Cloud Tasks

Funciones de alto nivel para encolar notificaciones. Cada función crea un task HTTP que invoca el endpoint correspondiente de la API de notificaciones.

**Importar:**

```python
from notifications_darp4 import (
    enqueue_notification_to_user,
    enqueue_notification_bulk,
    enqueue_notification_by_tenant,
    enqueue_notification_by_role,
)
```

**Funciones disponibles:**


| Función                            | Endpoint Target                                         | Descripción                                  |
| ---------------------------------- | ------------------------------------------------------- | -------------------------------------------- |
| `enqueue_notification_to_user()`   | `POST /notifications/send/{user_id}`                    | Notificación a un usuario específico         |
| `enqueue_notification_bulk()`      | `POST /notifications/send_bulk`                         | Notificación masiva a lista de usuarios      |
| `enqueue_notification_by_tenant()` | `POST /notifications/send_by_tenant/{tenant_id}`        | Notificación a todos los usuarios de un tenant |
| `enqueue_notification_by_role()`   | `POST /notifications/send_by_role/{tenant_id}/role/{role_name}` | Notificación por rol dentro de un tenant |


**Ejemplos:**

```python
# Notificación a un usuario
enqueue_notification_to_user(
    user_id="abc-123",
    title="Nueva orden",
    body="Tienes una nueva orden asignada",
    notif_type="order",
    data={"order_id": "ord-456"},
)

# Notificación masiva
enqueue_notification_bulk(
    user_ids=["user-1", "user-2", "user-3"],
    title="Mantenimiento programado",
    body="El sistema estará en mantenimiento mañana",
)

# Notificación a todo un tenant
enqueue_notification_by_tenant(
    tenant_id="tenant-abc",
    title="Actualización disponible",
    body="Hay una nueva versión de la app",
)

# Notificación por rol
enqueue_notification_by_role(
    tenant_id="tenant-abc",
    role_name="driver",
    title="Ruta actualizada",
    body="Tu ruta de hoy ha sido modificada",
    data={"route_id": "route-789"},
)

# Con ejecución diferida
from datetime import datetime, timedelta, timezone

enqueue_notification_to_user(
    user_id="abc-123",
    title="Recordatorio",
    body="Tu turno comienza en 30 minutos",
    schedule_time=datetime.now(timezone.utc) + timedelta(minutes=30),
)
```

**Parámetros comunes:**


| Parámetro       | Tipo             | Default  | Descripción                           |
| --------------- | ---------------- | -------- | ------------------------------------- |
| `title`         | `str`            | —        | Título de la notificación             |
| `body`          | `str`            | —        | Cuerpo de la notificación             |
| `notif_type`    | `str`            | `"info"` | Tipo de notificación                  |
| `data`          | `dict | None`    | `None`   | Datos adicionales                     |
| `schedule_time` | `datetime | None`| `None`   | Ejecución diferida (opcional)         |


**Variables de entorno:**


| Variable                   | Descripción                           | Default              |
| -------------------------- | ------------------------------------- | -------------------- |
| `NOTIFICATION_SERVICE_URL` | URL base del servicio de notificaciones | —                  |
| `NOTIFICATION_QUEUE_NAME`  | Nombre de la cola de Cloud Tasks      | `notification-queue` |


---

### `email_darp4` — Correos electrónicos

#### Template HTML

Genera correos HTML con branding de Darp4, logo, footer y enlace de baja.

**Importar:**

```python
from email_darp4.template import email_template
```

**Uso:**

```python
html = email_template(
    subject="Bienvenido",
    body="<p>Gracias por registrarte.</p>",
    to="usuario@ejemplo.com"
)
```

#### Envío por SMTP

Envía correos usando SMTP con el template integrado.

**Importar:**

```python
from email_darp4.send_email import send_email_smtp
```

**Ejemplo:**

```python
await send_email_smtp(
    from_email="noreply@darp4.com",
    to="usuario@ejemplo.com",
    subject="Confirmación de cuenta",
    body="<p>Haz clic en el enlace para activar tu cuenta.</p>",
    from_name="Darp4",
    reply_to="soporte@darp4.com"
)
```

**Variables de entorno:**


| Variable      | Descripción               |
| ------------- | ------------------------- |
| `SMTP_SERVER` | Servidor SMTP             |
| `SMTP_PORT`   | Puerto (ej. 465 para SSL) |
| `EMAIL_USER`  | Usuario SMTP              |
| `EMAIL_PASS`  | Contraseña SMTP           |


Incluye `List-Unsubscribe` y versión en texto plano.

---

## Variables de Entorno Resumidas


| Variable                                                        | Módulo                     | Obligatoria              |
| --------------------------------------------------------------- | -------------------------- | ------------------------ |
| `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `INSTANCE_CONNECTION_NAME` | database_darp4.session     | Sí                       |
| `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB`, `REDIS_PREFIX`          | database_darp4.redis       | No (hay defaults)        |
| `ENVIRONMENT`                                                   | session, signed_url, cloud_tasks | No (`local`)       |
| `BUCKET_NAME`, `TARGET_SA`                                      | signed_url                 | No (hay defaults)        |
| `SMTP_SERVER`, `SMTP_PORT`, `EMAIL_USER`, `EMAIL_PASS`          | send_email                 | Sí (para enviar correos) |
| `GCP_PROJECT_ID`, `GCP_LOCATION`, `GCP_SERVICE_ACCOUNT_EMAIL`   | cloud_tasks                | No (hay defaults)        |
| `NOTIFICATION_SERVICE_URL`, `NOTIFICATION_QUEUE_NAME`           | notifications_darp4        | Sí / No (hay default)    |


Usa un archivo `.env` en la raíz del proyecto y `python-dotenv` para cargarlas.

---

## Dependencias

Todas las dependencias están declaradas en `pyproject.toml` y se instalan automáticamente con el paquete:


| Paquete                | Versión                   | Módulo(s)                           |
| ---------------------- | ------------------------- | ----------------------------------- |
| `pydantic`             | >=2.0                     | schemas_darp4 (vía sqlmodel)        |
| `sqlmodel`             | >=0.0.14                  | schemas_darp4                       |
| `fastapi`              | >=0.100.0                 | logging_darp4                       |
| `sqlalchemy`           | >=2.0.0 (extras: asyncio) | database_darp4.session              |
| `asyncpg`              | >=0.28.0                  | database_darp4.session              |
| `redis`                | >=5.0.0                   | database_darp4.redis                |
| `python-dotenv`        | >=1.0.0                   | database_darp4.session, email_darp4 |
| `google-cloud-storage` | >=2.0.0                   | gcp_darp4.google_storage            |
| `google-cloud-tasks`   | >=2.0.0                   | gcp_darp4.cloud_tasks               |
| `google-auth`          | >=2.0.0                   | gcp_darp4.google_storage            |
| `httpx`                | >=0.27.0                  | gcp_darp4.cloud_tasks (fallback local) |


---

## Desarrollo

```bash
# Instalación editable
pip install -e .

# Ejecutar tests (cuando existan)
pytest
```

---

## Licencia

© 2026 Darp4. Cartagena, Colombia.
