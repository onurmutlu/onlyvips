#!/bin/bash
set -e

# OnlyVips "2 Dakika İçinde Prod'a Al" Scripti
# Bu script hızlı bir şekilde production'a deployment yapmayı sağlar

# Renk tanımlamaları
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonksiyonlar
show_header() {
    echo -e "\n${BLUE}=============================================${NC}"
    echo -e "${BLUE}   OnlyVips Hızlı Production Deployment   ${NC}"
    echo -e "${BLUE}=============================================${NC}\n"
}

show_step() {
    echo -e "\n${YELLOW}[ADIM $1] $2${NC}"
}

deployment_type=""

# Deployment tipini belirle
determine_deployment_type() {
    show_step "1" "Deployment ortamı belirleniyor..."
    
    if [ -n "$(command -v kubectl)" ] && [ -n "$(command -v helm)" ]; then
        echo "Kubernetes ve Helm tespit edildi."
        deployment_type="kubernetes"
    elif [ -f "docker-config/docker-compose.yml" ]; then
        echo "Docker Compose tespit edildi."
        deployment_type="docker"
    else
        echo -e "${RED}ERROR: Ne Kubernetes/Helm ne de Docker Compose ortamı tespit edilemedi!${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}Deployment tipi: ${deployment_type}${NC}"
}

# Ön kontroller
perform_prerequisites() {
    show_step "2" "Ön kontroller yapılıyor..."
    
    # Git repo kontrolü
    if [ ! -d ".git" ]; then
        echo -e "${RED}ERROR: Bu bir git repository değil. Lütfen ana proje dizininde olduğunuzdan emin olun.${NC}"
        exit 1
    fi
    
    # Main branch'de olup olmadığını kontrol et
    current_branch=$(git symbolic-ref --short HEAD 2>/dev/null)
    if [ "$current_branch" != "main" ] && [ "$current_branch" != "master" ]; then
        echo -e "${YELLOW}UYARI: Şu anda main/master branch'de değilsiniz. Şu anki branch: ${current_branch}${NC}"
        read -p "Devam etmek istiyor musunuz? (e/h): " confirm
        if [[ $confirm != [eE] ]]; then
            echo "İşlem iptal edildi."
            exit 0
        fi
    fi
    
    # Değişiklik kontrolü
    if [ -n "$(git status --porcelain)" ]; then
        echo -e "${YELLOW}UYARI: Commit edilmemiş değişiklikler var:${NC}"
        git status --short
        read -p "Devam etmek istiyor musunuz? (e/h): " confirm
        if [[ $confirm != [eE] ]]; then
            echo "İşlem iptal edildi."
            exit 0
        fi
    fi
    
    echo -e "${GREEN}Ön kontroller tamamlandı.${NC}"
}

# Kubernetes ile deployment
deploy_kubernetes() {
    show_step "3" "Kubernetes/Helm ile deployment hazırlanıyor..."
    
    # Namespace kontrolü
    namespace=${NAMESPACE:-"default"}
    if ! kubectl get namespace $namespace &>/dev/null; then
        echo "Namespace '$namespace' mevcut değil, oluşturuluyor..."
        kubectl create namespace $namespace
    fi
    
    # Release kontrolü
    release_name=${RELEASE_NAME:-"onlyvips"}
    if helm status $release_name -n $namespace &>/dev/null; then
        echo "Release '$release_name' zaten mevcut, güncelleme yapılacak."
        deployment_action="upgrade"
    else
        echo "Release '$release_name' mevcut değil, yeni kurulum yapılacak."
        deployment_action="install"
    fi
    
    # Production values.yaml
    if [ ! -f "charts/onlyvips-chart/values.yaml" ]; then
        echo -e "${RED}ERROR: values.yaml dosyası bulunamadı.${NC}"
        exit 1
    fi
    
    show_step "4" "Deployment yapılıyor..."
    echo "Helm $deployment_action işlemi başlatılıyor..."
    
    # Canary deployment mi?
    read -p "Canary deployment yapmak istiyor musunuz? (%10 trafik) (e/h): " use_canary
    if [[ $use_canary == [eE] ]]; then
        echo "Canary deployment başlatılıyor..."
        ./scripts/canary-deploy.sh
    else
        # Normal deployment
        if [ "$deployment_action" == "install" ]; then
            helm install $release_name ./charts/onlyvips-chart -n $namespace
        else
            helm upgrade $release_name ./charts/onlyvips-chart -n $namespace
        fi
    fi
}

# Docker Compose ile deployment
deploy_docker() {
    show_step "3" "Docker Compose ile deployment hazırlanıyor..."
    
    # Docker Compose dosyasını kontrol et
    if [ ! -f "docker-config/docker-compose.yml" ]; then
        echo -e "${RED}ERROR: docker-compose.yml dosyası bulunamadı.${NC}"
        exit 1
    fi
    
    # Mevcut imajları yedekle
    echo "Mevcut imajları yedekleniyor..."
    docker tag onlyvips/backend-api:latest onlyvips/backend-api:previous 2>/dev/null || true
    docker tag onlyvips/miniapp:latest onlyvips/miniapp:previous 2>/dev/null || true
    docker tag onlyvips/showcu-panel:latest onlyvips/showcu-panel:previous 2>/dev/null || true
    docker tag onlyvips/flirt-bot:latest onlyvips/flirt-bot:previous 2>/dev/null || true
    
    # docker-compose.yml dosyasını yedekle
    cp docker-config/docker-compose.yml docker-config/docker-compose.backup.yml
    
    show_step "4" "İmajlar oluşturuluyor ve deployment yapılıyor..."
    
    # Canary deployment mi?
    read -p "Canary deployment yapmak istiyor musunuz? (%10 trafik) (e/h): " use_canary
    if [[ $use_canary == [eE] ]]; then
        echo "Canary deployment başlatılıyor..."
        ./scripts/canary-deploy.sh
    else
        # Servisleri yeniden oluştur ve başlat
        cd docker-config
        docker-compose up -d --build
        cd ..
    fi
}

# Smoke testleri
run_smoke_tests() {
    show_step "5" "Smoke testleri çalıştırılıyor..."
    
    # Smoke test script'inin varlığını kontrol et
    if [ ! -f "scripts/smoke-test.sh" ]; then
        echo -e "${RED}ERROR: smoke-test.sh script'i bulunamadı.${NC}"
        exit 1
    fi
    
    echo "Servisler başlatıldı, smoke testleri çalıştırılıyor..."
    
    # Servislerin hazır olması için bekle (10 saniye)
    echo "Servislerin hazır olması için 10 saniye bekleniyor..."
    sleep 10
    
    # Smoke testleri çalıştır
    ./scripts/smoke-test.sh
    
    # Sonuçları kontrol et
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Smoke testleri başarılı!${NC}"
    else
        echo -e "${RED}✗ Smoke testleri başarısız oldu!${NC}"
        
        # Rollback sorusu
        read -p "Rollback yapmak istiyor musunuz? (e/h): " do_rollback
        if [[ $do_rollback == [eE] ]]; then
            echo "Rollback yapılıyor..."
            ./scripts/rollback.sh
            echo -e "${YELLOW}Rollback tamamlandı.${NC}"
            exit 1
        else
            echo -e "${YELLOW}Smoke testleri başarısız olmasına rağmen deployment devam ettiriliyor...${NC}"
        fi
    fi
}

# Kullanım rehberi ve notlar
show_usage_guide() {
    show_step "6" "Deployment tamamlandı"
    
    echo -e "${GREEN}OnlyVips Production deployment'ı başarıyla tamamlandı!${NC}"
    echo
    echo -e "${BLUE}=== ÖNEMLİ HATIRLATMALAR ===${NC}"
    echo -e "${YELLOW}1. Rollback komutu:${NC} ./scripts/rollback.sh"
    echo -e "${YELLOW}2. Servisleri izlemek için:${NC}"
    
    if [ "$deployment_type" == "kubernetes" ]; then
        echo "   kubectl get pods -n ${NAMESPACE:-default} -w"
        echo "   kubectl logs -f <pod-adı> -n ${NAMESPACE:-default}"
    else
        echo "   cd docker-config && docker-compose ps"
        echo "   docker-compose logs -f"
    fi
    
    echo
    echo -e "${YELLOW}3. Metrik izleme:${NC}"
    if [ "$deployment_type" == "kubernetes" ]; then
        echo "   kubectl port-forward svc/prometheus-server 9090:80 -n monitoring"
        echo "   kubectl port-forward svc/grafana 3000:80 -n monitoring"
    else
        echo "   Docker için metrik izleme: http://localhost:9090 (Prometheus kuruluysa)"
    fi
    
    echo
    echo -e "${BLUE}=== DESTEK VE YARDIM ===${NC}"
    echo -e "Problem durumunda: support@onlyvips.xyz"
    echo
}

# Ana script akışı
show_header
determine_deployment_type
perform_prerequisites

# Deployment tipi'ne göre deployment yap
if [ "$deployment_type" == "kubernetes" ]; then
    deploy_kubernetes
else
    deploy_docker
fi

# Smoke testleri çalıştır
run_smoke_tests

# Kullanım rehberini göster
show_usage_guide

echo -e "\n${GREEN}İşlem tamamlandı! OnlyVips production'da çalışıyor.${NC}"
exit 0 