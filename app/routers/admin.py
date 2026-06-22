import os
import subprocess
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database.connector import MongoConnector
from app.models.habit import HabitResponse
from app.services.habit_manager import HabitManager

router = APIRouter()


def get_db() -> AsyncIOMotorDatabase:
    return MongoConnector.get_database()


@router.get(
    "/habits",
    response_model=dict[str, Any],
    response_model_by_alias=False,
)
async def get_all_habits_admin(
    search: str | None = None,
    status: str | None = None,
    user_id: str | None = None,
    skip: int = 0,
    limit: int = 50,
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> dict[str, Any]:
    """
    Endpoint de admin para listar todos los hábitos con filtros, búsqueda y paginación.
    - search: Busca en nombre y frecuencia (case-insensitive regex)
    - status: Filtra por "active" o "archived"
    - user_id: Filtra por usuario
    - skip: Registros a saltar (para paginación)
    - limit: Máximo de registros a retornar
    """
    if skip < 0 or limit < 1 or limit > 200:
        raise HTTPException(
            status_code=400, detail="Parámetros de paginación inválidos")

    result = await HabitManager.list_all_habits_admin(
        db,
        search=search,
        status=status,
        user_id=user_id,
        skip=skip,
        limit=limit,
    )
    return result


@router.post("/backup", status_code=status.HTTP_200_OK)
async def create_backup(db: AsyncIOMotorDatabase = Depends(get_db)) -> dict[str, str]:
    """
    Crea un backup de la base de datos MongoDB.
    Retorna la ruta del archivo de backup.
    """
    try:
        # Obtener credenciales de MongoDB desde variables de entorno
        mongo_host = os.getenv("DB_HOST", "localhost")
        mongo_port = os.getenv("DB_PORT", "27017")
        mongo_user = os.getenv("DB_USER", "habits_app")
        mongo_pass = os.getenv("DB_PASS", "pruebatpfinal")
        mongo_db = os.getenv("DB_NAME", "habits_db")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = "backups"
        os.makedirs(backup_dir, exist_ok=True)
        backup_file = f"{backup_dir}/backup_{mongo_db}_{timestamp}"

        # Usar mongodump para realizar el backup
        cmd = [
            "mongodump",
            f"--host={mongo_host}:{mongo_port}",
            f"--username={mongo_user}",
            f"--password={mongo_pass}",
            f"--authenticationDatabase=admin",
            f"--db={mongo_db}",
            f"--out={backup_file}",
        ]

        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=60)

        if result.returncode != 0:
            raise RuntimeError(f"Backup failed: {result.stderr}")

        return {
            "status": "success",
            "message": f"Backup creado exitosamente en {backup_file}",
            "file": backup_file,
        }
    except FileNotFoundError:
        raise HTTPException(
            status_code=500,
            detail="mongodump no está instalado. Instala MongoDB Tools.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error en backup: {str(e)}")


@router.post("/restore", status_code=status.HTTP_200_OK)
async def restore_backup(
    backup_file: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> dict[str, str]:
    """
    Restaura una base de datos desde un backup.
    - backup_file: Ruta del archivo de backup (ej: backups/backup_habits_db_20260603_230000)
    """
    try:
        if not backup_file or not backup_file.startswith("backups/"):
            raise ValueError("Ruta de backup inválida")

        if not os.path.exists(backup_file):
            raise HTTPException(
                status_code=404, detail="Archivo de backup no encontrado")

        mongo_host = os.getenv("DB_HOST", "localhost")
        mongo_port = os.getenv("DB_PORT", "27017")
        mongo_user = os.getenv("DB_USER", "habits_app")
        mongo_pass = os.getenv("DB_PASS", "pruebatpfinal")

        # Usar mongorestore para restaurar el backup
        cmd = [
            "mongorestore",
            f"--host={mongo_host}:{mongo_port}",
            f"--username={mongo_user}",
            f"--password={mongo_pass}",
            f"--authenticationDatabase=admin",
            f"--drop",
            backup_file,
        ]

        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=60)

        if result.returncode != 0:
            raise RuntimeError(f"Restore failed: {result.stderr}")

        return {
            "status": "success",
            "message": f"Backup restaurado exitosamente desde {backup_file}",
            "file": backup_file,
        }
    except FileNotFoundError:
        raise HTTPException(
            status_code=500,
            detail="mongorestore no está instalado. Instala MongoDB Tools.",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error en restore: {str(e)}")


@router.get("/backups", status_code=status.HTTP_200_OK)
async def list_backups() -> dict[str, Any]:
    """
    Lista todos los backups disponibles.
    """
    backup_dir = "backups"
    if not os.path.exists(backup_dir):
        return {"backups": []}

    backups = []
    for item in os.listdir(backup_dir):
        path = os.path.join(backup_dir, item)
        if os.path.isdir(path):
            stat = os.stat(path)
            backups.append({
                "name": item,
                "path": path,
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            })

    backups.sort(key=lambda x: x["created"], reverse=True)
    return {"backups": backups}
