FROM python:3.10-slim

WORKDIR /app

# Sadece gerekli dosyaları kopyala
COPY requirements.txt .
COPY app/ ./app/
COPY main.py profile.py ./

# Bağımlılıkları yükle
RUN pip install --no-cache-dir -r requirements.txt

# Veritabanı ve upload dizinlerini oluştur
RUN mkdir -p uploads

# uWSGI ile çalıştır 
ENV PORT=5000
EXPOSE $PORT

CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--port=${PORT}", "--proxy-headers", "--workers=4"]