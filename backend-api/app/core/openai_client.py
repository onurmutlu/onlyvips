import os
import time
from typing import Dict, Optional
import openai
from app.core.config import settings

class OpenAIClient:
    """OpenAI API için optimize edilmiş istemci sınıfı"""
    
    # Kullanıcıların günlük kullanım miktarı
    _user_usage: Dict[str, int] = {}
    _last_reset = time.time()
    
    def __init__(self):
        """OpenAI API ile bağlantı kurma"""
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        self.max_usage_day = int(os.getenv("GPT_MAX_USAGE_DAY", "50"))
        self.max_tokens = int(os.getenv("GPT_MAX_TOKENS", "250"))
    
    def _check_and_reset_usage(self):
        """Günlük kullanım limitini sıfırlama kontrolü"""
        current_time = time.time()
        day_seconds = 24 * 60 * 60
        if current_time - self._last_reset > day_seconds:
            self._user_usage.clear()
            self._last_reset = current_time
    
    def can_use_gpt(self, user_id: str) -> bool:
        """Kullanıcının GPT kullanabilirliğini kontrol eder"""
        self._check_and_reset_usage()
        return self._user_usage.get(user_id, 0) < self.max_usage_day
    
    def get_completion(self, user_id: str, prompt: str) -> Optional[str]:
        """OpenAI API'den yanıt alır"""
        if not self.can_use_gpt(user_id):
            return None
            
        try:
            client = openai.OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens
            )
            
            # Kullanım sayacını artır
            self._user_usage[user_id] = self._user_usage.get(user_id, 0) + 1
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API hatası: {str(e)}")
            return None

# Tekil örnek oluştur
openai_client = OpenAIClient() 