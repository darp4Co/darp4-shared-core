import asyncio
import os
import firebase_admin
from firebase_admin import auth as firebase_auth, credentials
from firebase_admin.auth import (
    ExpiredIdTokenError,
    InvalidIdTokenError,
    RevokedIdTokenError,
    CertificateFetchError,
)
from logging import getLogger
from traceback import format_exc
from typing import Any
from schemas_darp4.firebase_session import FirebaseSessionSchema

logger = getLogger("uvicorn.error")


class FirebaseTokenValidator:
    """
    Clase encargada de validar los ID Tokens emitidos por Firebase Authentication
    utilizando el SDK oficial de Firebase Admin (firebase_admin.auth.verify_id_token).

     - project_id:    ID del proyecto de Firebase.
     - credential:    Credencial de Firebase Admin (por defecto usa Application Default
                      Credentials). Pasa un objeto credentials.Certificate si quieres
                      usar un Service Account JSON explícito.
     - app_name:      Nombre de la instancia de firebase_admin.App. Útil cuando
                      conviven múltiples proyectos en el mismo proceso.
     - check_revoked: Si es True, verifica que el token no haya sido revocado
                      consultando Firebase (requiere red). Por defecto False.
                      Se fuerza a False automáticamente en modo emulador.
     - emulator_host: Host del emulador de Firebase Auth (p.ej. "localhost:9099").
                      Si es None, se lee la variable de entorno FIREBASE_AUTH_EMULATOR_HOST.
                      Si ninguna está presente, se asume producción.

    uso recomendado:

        # Con Application Default Credentials (recomendado en Cloud Run / GKE):
        token_validator = FirebaseTokenValidator(project_id="my-firebase-project")

        # Con Service Account explícito:
        token_validator = FirebaseTokenValidator(
            project_id="my-firebase-project",
            credential=credentials.Certificate("path/to/serviceAccount.json")
        )

        # Con el emulador local (también funciona si FIREBASE_AUTH_EMULATOR_HOST está en el entorno):
        token_validator = FirebaseTokenValidator(
            project_id="demo-project",
            emulator_host="localhost:9099"
        )

        app.state.firebase_validator = token_validator

        session_data = await app.state.firebase_validator.validate(token="eyJhbGci...")

        opcional:
            cookie_schema = ApiKeyCookie(name="firebase_token", auto_error=True)

            async def get_firebase_user(
                request: Request,
                token: str = Depends(cookie_schema)
            ) -> FirebaseSessionSchema:
                validator: FirebaseTokenValidator = request.app.state.firebase_validator
                return await validator.validate(token=token)
    """

    __slots__ = ("_app", "_check_revoked", "_emulator_host")

    def __init__(
        self,
        project_id: str,
        credential: credentials.Base | None = None,
        app_name: str = firebase_admin._DEFAULT_APP_NAME,
        check_revoked: bool = False,
        emulator_host: str | None = None,
    ):
        """
        Inicializa la aplicación de Firebase Admin si aún no existe.
            - project_id:    ID del proyecto de Firebase.
            - credential:    Credencial a usar. Si es None usa Application Default Credentials.
            - app_name:      Nombre de la instancia de App (útil para multi-proyecto).
            - check_revoked: Verifica revocación del token en cada validación.
                             Se fuerza a False cuando se detecta el emulador.
            - emulator_host: Host del emulador (p.ej. "localhost:9099"). Si es None
                             se lee FIREBASE_AUTH_EMULATOR_HOST del entorno.
        """
        # Detectar modo emulador: parámetro explícito > variable de entorno
        self._emulator_host: str | None = (
            emulator_host or os.environ.get("FIREBASE_AUTH_EMULATOR_HOST")
        )

        if self._emulator_host:
            # El SDK de firebase-admin usa esta variable para redirigir al emulador.
            # Si ya estaba seteada en el entorno no hace falta sobreescribirla,
            # pero si se pasó por parámetro nos aseguramos de que esté disponible.
            os.environ.setdefault("FIREBASE_AUTH_EMULATOR_HOST", self._emulator_host)
            # El emulador no soporta verificación de revocación.
            self._check_revoked = False
            logger.info(
                f"FirebaseTokenValidator iniciado en modo EMULADOR "
                f"(host={self._emulator_host})"
            )
        else:
            self._check_revoked: bool = check_revoked

        try:
            self._app: firebase_admin.App = firebase_admin.get_app(name=app_name)
        except ValueError:
            # La app aún no fue inicializada — la creamos
            cred = credential or credentials.ApplicationDefault()
            self._app = firebase_admin.initialize_app(
                credential=cred,
                options={"projectId": project_id},
                name=app_name,
            )

    @property
    def is_emulator(self) -> bool:
        """Retorna True si el validador está operando contra el emulador de Firebase Auth."""
        return self._emulator_host is not None

    async def validate(self, token: str) -> FirebaseSessionSchema:
        """
        Valida un ID Token de Firebase usando el SDK de Firebase Admin.
        El SDK se encarga de:
            - Obtener y cachear los certificados públicos de Firebase.
            - Verificar la firma (RS256).
            - Verificar expiración, issuer y audience automáticamente.
            - Opcionalmente verificar si el token fue revocado.

        En modo emulador:
            - FIREBASE_AUTH_EMULATOR_HOST dirige las peticiones al emulador local.
            - La verificación de firma se omite (los tokens del emulador no
              están firmados con claves de producción).
            - check_revoked se fuerza a False.

            - token: ID Token de Firebase a validar.
            Retorna un FirebaseSessionSchema con el payload decodificado.
            Lanza una excepción si la validación falla.
        """
        try:
            payload: dict[str, Any] = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: firebase_auth.verify_id_token(
                    id_token=token,
                    app=self._app,
                    check_revoked=self._check_revoked,
                ),
            )
            return FirebaseSessionSchema(**payload)

        except ExpiredIdTokenError:
            logger.warning("Firebase token expirado")
            raise
        except RevokedIdTokenError:
            logger.warning("Firebase token revocado")
            raise
        except InvalidIdTokenError as e:
            logger.error(f"Firebase token inválido: {e}")
            raise
        except CertificateFetchError as e:
            logger.error(f"Error al obtener certificados de Firebase: {e}")
            raise
        except Exception as e:
            logger.error(f"Error inesperado validando Firebase token: {e}\n{format_exc()}")
            raise
