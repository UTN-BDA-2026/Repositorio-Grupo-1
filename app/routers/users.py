from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_users() -> list[dict[str, str]]:
    # Placeholder de endpoint; aún no se implementa persistencia de usuarios.
    return []
