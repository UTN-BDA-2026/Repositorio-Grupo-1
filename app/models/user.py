from pydantic import BaseModel, ConfigDict, Field, StrictStr


class UserBase(BaseModel):
    # Bloquea campos extra y recorta espacios en cadenas de entrada.
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    username: StrictStr = Field(min_length=3, max_length=40)


class UserCreate(UserBase):
    # Modelo de entrada para crear usuarios.
    pass


class UserResponse(UserBase):
    # Modelo de salida con identificador serializado.
    id: str
