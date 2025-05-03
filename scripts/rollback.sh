#!/bin/bash
set -e

# OnlyVips Rollback Script
# Bu script production deployment'ı önceki kararlı sürüme geri döndürür

# Renk tanımlamaları
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}OnlyVips Rollback başlatılıyor...${NC}"

# Ortam değişkenleri
RELEASE_NAME=${RELEASE_NAME:-"onlyvips"}
NAMESPACE=${NAMESPACE:-"default"}
REVISION=${1:-""} # İsteğe bağlı belirli bir revizyon

# Rollback işlemi
echo -e "${YELLOW}Rollback işlemi başlatılıyor...${NC}"

# Kubernetes/Helm ile deployment kontrolü
if [ -n "$(command -v kubectl)" ] && [ -n "$(command -v helm)" ]; then
    echo "Helm ile rollback yapılıyor..."
    
    # Eğer belirli bir revizyon belirtilmişse, o revizyona döndür
    if [ -n "$REVISION" ]; then
        helm rollback ${RELEASE_NAME} ${REVISION} -n ${NAMESPACE}
    else
        # Önceki revizyona geri dön
        PREVIOUS_REVISION=$(helm history ${RELEASE_NAME} -n ${NAMESPACE} | tail -2 | head -1 | awk '{print $1}')
        
        if [ -n "$PREVIOUS_REVISION" ]; then
            echo "Önceki revizyon ${PREVIOUS_REVISION}'e geri dönülüyor..."
            helm rollback ${RELEASE_NAME} ${PREVIOUS_REVISION} -n ${NAMESPACE}
        else
            echo -e "${RED}Önceki revizyon bulunamadı!${NC}"
            exit 1
        fi
    fi
    
    echo -e "${GREEN}Helm rollback başarıyla tamamlandı!${NC}"
    
# Docker Compose ile deployment kontrolü
elif [ -f "docker-config/docker-compose.yml" ]; then
    echo "Docker Compose ile rollback yapılıyor..."
    
    cd docker-config
    
    # Mevcut servisleri durdur
    docker-compose down
    
    # Önceki imajları kontrol et
    if docker image inspect onlyvips/backend-api:previous >/dev/null 2>&1; then
        # Önceki imajları geri yükle
        docker tag onlyvips/backend-api:previous onlyvips/backend-api:latest
        docker tag onlyvips/miniapp:previous onlyvips/miniapp:latest
        docker tag onlyvips/showcu-panel:previous onlyvips/showcu-panel:latest
        docker tag onlyvips/flirt-bot:previous onlyvips/flirt-bot:latest
        
        # Servisleri yeniden başlat
        docker-compose up -d
        
        echo -e "${GREEN}Docker Compose rollback başarıyla tamamlandı!${NC}"
    else
        echo -e "${RED}Önceki imajlar bulunamadı! 'previous' etiketli imajlar mevcut değil.${NC}"
        
        # Fallback: Eğer backup docker-compose dosyası varsa onu kullan
        if [ -f "docker-compose.backup.yml" ]; then
            echo "Backup docker-compose dosyası bulundu, bu kullanılıyor..."
            docker-compose -f docker-compose.backup.yml up -d
            echo -e "${GREEN}Backup konfigürasyonuyla rollback tamamlandı!${NC}"
        else
            echo -e "${RED}Rollback yapılamadı! Ne önceki imajlar ne de backup konfigürasyonu mevcut.${NC}"
            exit 1
        fi
    fi
else
    echo -e "${RED}Deployment ortamı tanımlanamadı. Kubectl/Helm veya Docker Compose gerekli!${NC}"
    exit 1
fi

echo "Rollback işlemi tamamlandı: $(date)"

# Sağlık kontrolü
echo "Servis sağlık kontrolü yapılıyor..."

if [ -n "$(command -v kubectl)" ]; then
    echo "Kubernetes servisleri kontrol ediliyor..."
    kubectl get pods -n ${NAMESPACE} -l release=${RELEASE_NAME}
elif [ -f "docker-config/docker-compose.yml" ]; then
    echo "Docker servisleri kontrol ediliyor..."
    docker-compose ps
fi

echo -e "${GREEN}Rollback işlemi tamamlandı. Lütfen servisleri manuel olarak kontrol edin.${NC}"

exit 0 