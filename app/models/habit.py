from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StrictStr


class HabitBase(BaseModel):
    # Rechaza claves no definidas (incluyendo payloads de operadores maliciosos) y limpia espacios.
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: StrictStr = Field(min_length=1, max_length=120)
    frequency: StrictStr = Field(min_length=1, max_length=60)
    status: Literal["active", "archived"] = "active"


class HabitCreate(HabitBase):
    # Modelo específico de alta; hereda validaciones de la base.
    pass


class HabitResponse(HabitBase):
    # Permite poblar el campo `id` a partir del alias `_id` de MongoDB.
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        populate_by_name=True,
    )

    id: str = Field(alias="_id")
    user_id: StrictStr | None = None
    date: datetime | None = None
