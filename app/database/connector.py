import os
from urllib.parse import quote_plus

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import PyMongoError


class MongoConnector:
    # Cachea cliente y base para reutilizar conexión en todo el proceso.
    _client: AsyncIOMotorClient | None = None
    _database: AsyncIOMotorDatabase | None = None

    @classmethod
    def _build_uri(cls) -> tuple[str, str]:
        # Obtiene configuración base desde variables de entorno.
        db_user = os.getenv("DB_USER")
        db_pass = os.getenv("DB_PASS")
        db_host = os.getenv("DB_HOST")
        db_name = os.getenv("DB_NAME", "habits_db")
        db_protocol = os.getenv("DB_PROTOCOL", "mongodb+srv")
        direct_env = os.getenv("DB_DIRECT_CONNECTION")

        if not db_host:
            raise ValueError("DB_HOST environment variable is required")

        # Incluye credenciales solo cuando ambas están disponibles.
        credentials = ""
        if db_user and db_pass:
            credentials = f"{quote_plus(db_user)}:{quote_plus(db_pass)}@"

        options = ["retryWrites=true", "w=majority"]
        if direct_env is None:
            direct_enabled = db_protocol == "mongodb" and db_host.startswith(
                ("localhost", "127.0.0.1")
            )
        else:
            direct_enabled = direct_env.strip().lower() in {"1", "true", "yes", "on"}

        if direct_enabled:
            options.append("directConnection=true")

        uri = f"{db_protocol}://{credentials}{db_host}/{db_name}?{'&'.join(options)}"
        return uri, db_name

    @classmethod
    def get_database(cls) -> AsyncIOMotorDatabase:
        if cls._database is not None:
            return cls._database

        try:
            # Crea cliente y selecciona base una sola vez.
            uri, db_name = cls._build_uri()
            tls_env = os.getenv("DB_TLS")
            if tls_env is None:
                tls_enabled = uri.startswith("mongodb+srv://")
            else:
                tls_enabled = tls_env.strip().lower() in {"1", "true", "yes", "on"}

            cls._client = AsyncIOMotorClient(uri, tls=tls_enabled)
            cls._database = cls._client[db_name]
            return cls._database
        except (ValueError, PyMongoError) as exc:
            raise ConnectionError(
                "Could not establish MongoDB connection with the provided environment configuration"
            ) from exc
