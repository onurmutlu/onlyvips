from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Task(BaseModel):
    id: int
    title: str
    reward: int

@app.get("/tasks/list")
def get_tasks():
    return {
        "tasks": [
            {"id": 1, "title": "DM Gönder", "reward": 5},
            {"id": 2, "title": "Yeni Üye Davet Et", "reward": 10},
            {"id": 3, "title": "Yorum Yap", "reward": 3}
        ]
    }

@app.get("/stars/balance")
def get_balance(user_id: str = "demo"):
    return {"user_id": user_id, "stars": 42}

@app.post("/stars/spend")
def spend_stars(user_id: str, amount: int):
    return {"user_id": user_id, "stars_remaining": max(0, 42 - amount)}

@app.get("/profile/badges")
def get_badges(user_id: str = "demo"):
    return {"user_id": user_id, "badges": ["rozet-1", "rozet-2"]}

@app.get("/profile/{user_id}")
def get_profile(user_id: str):
    return {"user_id": user_id, "name": "VIP Kullanıcı", "level": 5}
