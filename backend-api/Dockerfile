FROM python:3.13-slim AS builder

WORKDIR /app

# Geliştirme araçlarını ve derleme bağımlılıklarını yükle
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Sanal ortam oluştur ve etkinleştir
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Bağımlılıkları kopyala ve yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.13-slim AS runtime

WORKDIR /app

# Sanal ortamı kopyala
COPY --from=builder /venv /venv
ENV PATH="/venv/bin:$PATH"

# Uygulama kodlarını kopyala
COPY ./app ./app
COPY ./alembic.ini .
COPY ./pyproject.toml .

# Log ve uploads dizinleri oluştur
RUN mkdir -p logs uploads

# Kullanıcı oluştur
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Ortam değişkenlerini ayarla
ENV PYTHONPATH="/app"
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Port aç
EXPOSE 8000

# Sağlık kontrol dosyası oluştur
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8000/health || exit 1

# Uygulamayı çalıştır
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]