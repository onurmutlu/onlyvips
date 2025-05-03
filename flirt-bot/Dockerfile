FROM python:3.11-slim AS builder

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
FROM python:3.11-slim AS runtime

WORKDIR /app

# Sanal ortamı kopyala
COPY --from=builder /venv /venv
ENV PATH="/venv/bin:$PATH"

# Çalışma zamanı bağımlılıkları
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Uygulama kodlarını kopyala
COPY ./src ./src
COPY ./bot_listener.py .

# Log ve sessions dizinleri oluştur
RUN mkdir -p logs sessions

# Kullanıcı oluştur
RUN useradd -m botuser && chown -R botuser:botuser /app
USER botuser

# Ortam değişkenlerini ayarla
ENV PYTHONPATH="/app"
ENV PYTHONUNBUFFERED=1

# Sağlık kontrol script'i ekle
COPY --chown=botuser:botuser ./healthcheck.py .
HEALTHCHECK --interval=60s --timeout=10s --start-period=20s --retries=3 \
    CMD ["python", "healthcheck.py"]

# Botu çalıştır
CMD ["python", "bot_listener.py"] 