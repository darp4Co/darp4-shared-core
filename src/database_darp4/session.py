import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession
from sqlalchemy.orm import sessionmaker


load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")
INSTANCE_CONNECTION_NAME = os.getenv("INSTANCE_CONNECTION_NAME")

if not all([DB_USER, DB_PASSWORD, DB_NAME, DB_HOST, INSTANCE_CONNECTION_NAME]):
    raise RuntimeError("Faltan variables de entorno para la DB")

DB_SOCKET_DIR = "/cloudsql"
DB_HOST = f"{DB_SOCKET_DIR}/{INSTANCE_CONNECTION_NAME}"
ENVIRONMENT = os.getenv("ENVIRONMENT", "local")  # local | cloud

if ENVIRONMENT == "cloud":
    DATABASE_URL = (
        f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@/"
        f"{DB_NAME}?host=/cloudsql/{INSTANCE_CONNECTION_NAME}"
    )
else:
    DATABASE_URL = (
        f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@"
        f"{DB_HOST}:5432/{DB_NAME}"
    )

_engine: AsyncEngine | None = None


def get_engine() -> AsyncEngine:
    """
    Obtiene una instancia global de conexión asíncrona a la base de datos.

    Si la conexión no ha sido creada previamente, se inicializa utilizando la configuración 
    definida por las variables de entorno: DATABASE_URL.

    #### Args:
        None

    #### Returns:
        AsyncEngine: Instancia asíncrona de SQLAlchemy para realizar consultas a la base de datos.

    #### Raises:
        RuntimeError: Si las variables de entorno no están configuradas correctamente.
    """
    global _engine

    print(DATABASE_URL)  # Debug: Imprime la URL de la base de datos para verificar su formato

    if _engine is None:
        _engine = create_async_engine(
            DATABASE_URL,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800,
            pool_pre_ping=True,
            echo=False,
            future=True
        )

    return _engine


async_session_maker = sessionmaker(
    bind=get_engine(),
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session():
    """
    Dependency-style generator.
    """
    async with async_session_maker() as session:
        yield session
