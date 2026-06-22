from datetime import UTC, datetime
from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.habit import HabitCreate, HabitResponse


class HabitManager:
    @staticmethod
    async def list_habits(db: AsyncIOMotorDatabase) -> list[HabitResponse]:
        # Consulta hábitos y transforma cada documento a modelo de respuesta.
        cursor = db.habits.find().sort("date", -1)
        habits: list[HabitResponse] = []
        async for item in cursor:
            habits.append(HabitResponse(**_serialize_habit(item)))
        return habits

    @staticmethod
    async def create_habit(db: AsyncIOMotorDatabase, habit: HabitCreate) -> HabitResponse:
        # Agrega timestamp UTC antes de guardar y reconsulta el documento creado.
        payload = habit.model_dump()
        payload["date"] = datetime.now(UTC)
        insert_result = await db.habits.insert_one(payload)
        created = await db.habits.find_one({"_id": insert_result.inserted_id})
        if created is None:
            raise RuntimeError("Habit creation failed")
        return HabitResponse(**_serialize_habit(created))

    @staticmethod
    async def delete_habit(db: AsyncIOMotorDatabase, habit_id: str) -> bool:
        # Elimina un hábito por ID.
        try:
            result = await db.habits.delete_one({"_id": ObjectId(habit_id)})
            return result.deleted_count > 0
        except Exception:
            return False

    @staticmethod
    async def archive_habit(db: AsyncIOMotorDatabase, habit_id: str) -> HabitResponse | None:
        # Cambia el estado de un hábito a "archived".
        try:
            updated = await db.habits.find_one_and_update(
                {"_id": ObjectId(habit_id)},
                {"$set": {"status": "archived"}},
                return_document=True
            )
            if updated is None:
                return None
            return HabitResponse(**_serialize_habit(updated))
        except Exception:
            return None

    @staticmethod
    async def list_all_habits_admin(
        db: AsyncIOMotorDatabase,
        search: str | None = None,
        status: str | None = None,
        user_id: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> dict[str, Any]:
        # Consulta de admin con filtros, búsqueda, paginación.
        query: dict[str, Any] = {}

        if search:
            query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"frequency": {"$regex": search, "$options": "i"}},
            ]

        if status and status in ["active", "archived"]:
            query["status"] = status

        if user_id:
            query["user_id"] = user_id

        total = await db.habits.count_documents(query)
        cursor = db.habits.find(query).sort("date", -1).skip(skip).limit(limit)

        habits: list[HabitResponse] = []
        async for item in cursor:
            habits.append(HabitResponse(**_serialize_habit(item)))

        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "items": habits,
        }


def _serialize_habit(document: dict[str, Any]) -> dict[str, Any]:
    # Convierte ObjectId a string para que sea serializable en JSON.
    if isinstance(document.get("_id"), ObjectId):
        document["_id"] = str(document["_id"])
    return document
