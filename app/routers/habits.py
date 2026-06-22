from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database.connector import MongoConnector
from app.models.habit import HabitCreate, HabitResponse
from app.services.habit_manager import HabitManager

router = APIRouter()


def get_db() -> AsyncIOMotorDatabase:
    # Dependencia compartida para entregar la base de datos en cada request.
    return MongoConnector.get_database()


@router.get("/", response_model=list[HabitResponse], response_model_by_alias=False)
async def get_habits(db: AsyncIOMotorDatabase = Depends(get_db)) -> list[HabitResponse]:
    # Lista hábitos ordenados por fecha de creación descendente.
    return await HabitManager.list_habits(db)


@router.post(
    "/",
    response_model=HabitResponse,
    response_model_by_alias=False,
    status_code=status.HTTP_201_CREATED,
)
async def create_habit(
    habit: HabitCreate,
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> HabitResponse:
    # Crea un hábito nuevo y devuelve el documento persistido.
    return await HabitManager.create_habit(db, habit)


@router.delete("/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_habit(
    habit_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> None:
    # Elimina un hábito por ID.
    deleted = await HabitManager.delete_habit(db, habit_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Hábito no encontrado")


@router.patch("/{habit_id}/archive", response_model=HabitResponse, response_model_by_alias=False)
async def archive_habit(
    habit_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> HabitResponse:
    # Cambia el estado de un hábito a "archived".
    updated = await HabitManager.archive_habit(db, habit_id)
    if updated is None:
        raise HTTPException(status_code=404, detail="Hábito no encontrado")
    return updated
