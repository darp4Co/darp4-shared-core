from redis.asyncio import Redis
import os
import random


REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_PREFIX = os.getenv("REDIS_PREFIX", "dev:")
CACHE_TTL_MEDIUM = int(os.getenv("CACHE_TTL_MEDIUM", 300)) + random.randint(0, 30)  # 5 minutos
CACHE_TTL_SHORT = int(os.getenv("CACHE_TTL_SHORT", 60)) + random.randint(0, 30)  # 1 minuto
CACHE_TTL_LONG = int(os.getenv("CACHE_TTL_LONG", 86400)) + random.randint(0, 30)  # 24 horas

redis: Redis | None = None


async def get_redis() -> Redis:
    """
    Obtiene una instancia global de conexión asíncrona a Redis.

    Si la conexión no ha sido creada previamente, se inicializa utilizando la configuración 
    definida por las variables de entorno: REDIS_HOST, REDIS_PORT y REDIS_DB. 
    Además, la conexión es codificada para retornar respuestas como strings en vez de bytes.

    #### Args:
        None

    #### Returns:
        Redis: Instancia asíncrona de Redis lista para ser utilizada en operaciones de caché o persistencia.

    #### Raises:
        RuntimeError: Si las variables de entorno no están configuradas correctamente.
    """
    global redis
    if redis is None:
        redis = Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True,
        )
    return redis
