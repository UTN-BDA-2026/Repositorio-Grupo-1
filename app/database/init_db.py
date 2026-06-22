from pymongo import DESCENDING

from app.database.connector import MongoConnector


async def init_indexes() -> None:
    # Índice para listados por usuario y fecha descendente.
    db = MongoConnector.get_database()
    await db.habits.create_index([("user_id", 1), ("date", DESCENDING)])
    # Índice parcial para acelerar búsquedas de hábitos activos por nombre.
    await db.habits.create_index(
        [("name", 1)],
        partialFilterExpression={"status": "active"},
    )
    # TTL para limpiar eventos efímeros luego de 24 horas.
    await db.ephemeral_events.create_index("created_at", expireAfterSeconds=86400)
