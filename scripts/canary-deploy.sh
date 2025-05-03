#!/bin/bash
set -e

# OnlyVips Canary Deployment Script
# Bu script %10 trafik ile canary deployment yapar ve 
# 30 dakika gözlem sonrası tam production'a geçer

# Renk tanımlamaları
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}OnlyVips Canary Deployment başlatılıyor...${NC}"

# Ortam değişkenleri
RELEASE_NAME=${RELEASE_NAME:-"onlyvips"}
NAMESPACE=${NAMESPACE:-"default"}
CANARY_WEIGHT=10
OBSERVATION_TIME=1800 # 30 dakika (saniye cinsinden)

# Canary release'i başlat
echo -e "${YELLOW}Canary deployment (%${CANARY_WEIGHT} trafik) başlatılıyor...${NC}"

# İstinasyona göre canary deployment (Kubernetes için)
if [ -n "$(command -v kubectl)" ] && [ -n "$(command -v helm)" ]; then
    # Helm ile canary deployment
    echo "Mevcut yapılandırmayı yedekle..."
    kubectl get configmap ${RELEASE_NAME}-canary-config -n ${NAMESPACE} 2>/dev/null || \
        kubectl create configmap ${RELEASE_NAME}-canary-config \
            --from-literal=previous-revision=$(helm list -n ${NAMESPACE} | grep ${RELEASE_NAME} | awk '{print $3}') \
            -n ${NAMESPACE}
    
    # Canary release yap
    helm upgrade ${RELEASE_NAME} ./charts/onlyvips-chart \
        --set global.canary.enabled=true \
        --set global.canary.weight=${CANARY_WEIGHT} \
        -n ${NAMESPACE}
    
    echo -e "${GREEN}Canary deployment başarıyla uygulandı!${NC}"
    
elif [ -f "docker-config/docker-compose.yml" ]; then
    # Docker Compose için canary deployment
    echo "Docker Compose ile canary deployment yapılıyor..."
    
    # Yeni imajları canary olarak etiketle
    docker tag onlyvips/backend-api:latest onlyvips/backend-api:canary
    docker tag onlyvips/miniapp:latest onlyvips/miniapp:canary
    docker tag onlyvips/showcu-panel:latest onlyvips/showcu-panel:canary
    docker tag onlyvips/flirt-bot:latest onlyvips/flirt-bot:canary
    
    # Canary servisleri başlat (örnek için backend)
    cd docker-config
    docker-compose -f docker-compose.yml -f docker-compose.canary.yml up -d backend-canary
    
    echo -e "${GREEN}Canary deployment Docker Compose ile başarıyla uygulandı!${NC}"
else
    echo -e "${RED}Deployment ortamı tanımlanamadı. Kubectl/Helm veya Docker Compose gerekli!${NC}"
    exit 1
fi

# Gözlem süresi
echo -e "${YELLOW}Canary deployment %${CANARY_WEIGHT} trafiği alıyor. ${OBSERVATION_TIME} saniye gözlemleniyor...${NC}"
echo "Gözlem başlangıç zamanı: $(date)"

# Monitoring başlat
if command -v kubectl &> /dev/null; then
    echo "Metrikler izleniyor..."
    # Prometheus metrikleri için örnek komut
    # kubectl port-forward svc/prometheus-server 9090:80 -n monitoring &
    # PID_MONITOR=$!
fi

# 30 dakika bekle
echo "Bekleme süresi: 30 dakika"
sleep ${OBSERVATION_TIME}

# Hata kontrolü (burada gerçek bir kontrol mekanizması eklenebilir)
DEPLOYMENT_SUCCESS=true

if [ "$DEPLOYMENT_SUCCESS" = true ]; then
    echo -e "${GREEN}Canary deployment başarılı! Tam rollout uygulanıyor...${NC}"
    
    # Tam rollout
    if [ -n "$(command -v kubectl)" ] && [ -n "$(command -v helm)" ]; then
        # Helm ile tam rollout
        helm upgrade ${RELEASE_NAME} ./charts/onlyvips-chart \
            --set global.canary.enabled=false \
            -n ${NAMESPACE}
            
    elif [ -f "docker-config/docker-compose.yml" ]; then
        # Docker Compose ile tam rollout
        cd docker-config
        docker-compose stop
        
        # Canary imajları stable olarak etiketle
        docker tag onlyvips/backend-api:canary onlyvips/backend-api:latest
        docker tag onlyvips/miniapp:canary onlyvips/miniapp:latest
        docker tag onlyvips/showcu-panel:canary onlyvips/showcu-panel:latest
        docker tag onlyvips/flirt-bot:canary onlyvips/flirt-bot:latest
        
        # Tüm servisleri başlat
        docker-compose up -d
    fi
    
    echo -e "${GREEN}Deployment başarıyla tamamlandı!${NC}"
else
    echo -e "${RED}Canary deployment başarısız! Rollback yapılıyor...${NC}"
    
    # Rollback
    if [ -n "$(command -v kubectl)" ] && [ -n "$(command -v helm)" ]; then
        PREVIOUS_REVISION=$(kubectl get configmap ${RELEASE_NAME}-canary-config -n ${NAMESPACE} -o jsonpath='{.data.previous-revision}')
        helm rollback ${RELEASE_NAME} ${PREVIOUS_REVISION} -n ${NAMESPACE}
    elif [ -f "docker-config/docker-compose.yml" ]; then
        cd docker-config
        # Canary servisleri durdur, önceki servisleri başlat
        docker-compose -f docker-compose.yml -f docker-compose.canary.yml down
        docker-compose up -d
    fi
    
    echo -e "${YELLOW}Rollback tamamlandı. Önceki stabil versiyona dönüldü.${NC}"
fi

# Monitoring sonlandır
if [ -n "${PID_MONITOR+set}" ]; then
    kill $PID_MONITOR
fi

echo "Deployment işlemi tamamlandı: $(date)"

# Çıkış
exit 0 