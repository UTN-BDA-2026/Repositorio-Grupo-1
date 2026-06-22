import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.init_db import init_indexes
from app.routers import admin, habits, users

# Carga variables del archivo .env para inicializar la app con configuración local.
load_dotenv()


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Prepara índices de MongoDB al arrancar y libera control al cerrar.
    await init_indexes()
    yield


app = FastAPI(title="Habit Tracker API", lifespan=lifespan)

# Permite configurar múltiples orígenes CORS separados por coma.
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip()
                   for origin in cors_origins if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(habits.router, prefix="/api/habits", tags=["habits"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])


@app.get("/health")
async def health() -> dict[str, str]:
    # Endpoint liviano para verificar disponibilidad del servicio.
    return {"status": "ok"}
