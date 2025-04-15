import requests
import json
import time

# API URL (bu örnekte yerel geliştirme ortamı kullanılıyor)
API_BASE_URL = "http://localhost:5000/api"

def chat_with_ai(user_id, prompt):
    """Yapay Zeka ile konuşma örneği"""
    url = f"{API_BASE_URL}/ai/chat"
    
    payload = {
        "user_id": user_id,
        "prompt": prompt
    }
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Hata: {response.status_code}")
        return None

def get_usage_stats(user_id):
    """Kullanıcı GPT kullanım istatistiklerini kontrol etme"""
    url = f"{API_BASE_URL}/ai/usage/{user_id}"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Hata: {response.status_code}")
        return None

def main():
    user_id = "test_user"
    
    # Kullanım istatistiklerini göster
    usage = get_usage_stats(user_id)
    print("Başlangıç kullanım durumu:")
    print(json.dumps(usage, indent=2))
    
    # GPT limiti aşılıncaya kadar birkaç soru sor
    prompts = [
        "Merhaba, nasılsın?",
        "İstanbul'da görülmesi gereken yerler nerelerdir?",
        "Türk mutfağının en iyi yemekleri nelerdir?",
        "Python programlama dilinin avantajları nelerdir?",
        "Yapay zeka hangi alanlarda kullanılabilir?",
        "Kripto para nedir?",
        "2023 yılında dünyada neler oldu?",
        "Fitness için başlangıç tavsiyeleri verebilir misin?",
        "Türkiye'nin iklimi nasıldır?",
        "En iyi film önerilerin neler?"
    ]
    
    for i, prompt in enumerate(prompts):
        print(f"\n--- Soru {i+1}: {prompt} ---")
        
        # Kullanım limitini kontrol et
        usage = get_usage_stats(user_id)
        if not usage["can_use"]:
            print("Günlük kullanım limiti aşıldı! Daha fazla soru sorulamaz.")
            break
            
        # Yapay zekaya soru sor
        result = chat_with_ai(user_id, prompt)
        
        if result and result["status"] == "success":
            print(f"Yanıt: {result['message']}")
            print(f"Günlük kullanım: {result['daily_usage']}/{result['daily_limit']}")
        elif result and result["status"] == "limit_exceeded":
            print(f"Limit aşıldı: {result['message']}")
            break
        else:
            print("Bir hata oluştu.")
        
        # API istekleri arasında biraz bekle
        time.sleep(1)
    
    # Son kullanım istatistiklerini göster
    usage = get_usage_stats(user_id)
    print("\nSon kullanım durumu:")
    print(json.dumps(usage, indent=2))

if __name__ == "__main__":
    main() 