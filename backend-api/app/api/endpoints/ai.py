from fastapi import APIRouter, Depends, HTTPException, Request
from app.core.openai_client import openai_client
from typing import Dict, Any, Optional

router = APIRouter()

@router.post("/chat")
async def chat_with_ai(request: Request) -> Dict[str, Any]:
    """OpenAI API ile sohbet endpoint'i
    
    Bu endpoint, kullanıcının OpenAI API ile sohbet etmesini sağlar.
    Kullanıcının günlük kullanım limiti kontrol edilir.
    """
    data = await request.json()
    user_id = str(data.get("user_id"))
    prompt = data.get("prompt")
    
    if not user_id or not prompt:
        raise HTTPException(status_code=400, detail="user_id ve prompt alanları gereklidir")
    
    # GPT kullanabilirlik kontrolü
    if not openai_client.can_use_gpt(user_id):
        return {
            "status": "limit_exceeded",
            "message": "Günlük GPT kullanım limitiniz doldu. Yarın tekrar deneyin."
        }
    
    # OpenAI cevabını al
    response = openai_client.get_completion(user_id, prompt)
    
    if response is None:
        return {
            "status": "error",
            "message": "OpenAI API yanıt vermedi. Lütfen daha sonra tekrar deneyin."
        }
    
    return {
        "status": "success",
        "message": response,
        "daily_usage": openai_client._user_usage.get(user_id, 0),
        "daily_limit": openai_client.max_usage_day
    }

@router.get("/usage/{user_id}")
async def get_user_usage(user_id: str) -> Dict[str, Any]:
    """Kullanıcının günlük GPT kullanım miktarını döndürür"""
    openai_client._check_and_reset_usage()
    
    usage = openai_client._user_usage.get(user_id, 0)
    remaining = max(0, openai_client.max_usage_day - usage)
    
    return {
        "user_id": user_id,
        "daily_usage": usage,
        "daily_limit": openai_client.max_usage_day,
        "remaining": remaining,
        "can_use": usage < openai_client.max_usage_day
    } 