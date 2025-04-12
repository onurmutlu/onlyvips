from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

users_db = {
    "demo123": {"username": "demo123", "xp": 85, "badges": ["Rozet-1", "Rozet-2"]},
    "onlyvips": {"username": "onlyvips", "xp": 30, "badges": []}
}

@router.get("/profile/{username}")
async def get_profile(username: str):
    user = users_db.get(username)
    if not user:
        return JSONResponse(status_code=404, content={"error": "Kullanıcı bulunamadı"})
    return user
