#!/bin/bash
set -e

# OnlyVips Smoke Test Script
# Bu script production deployment sonrası temel sağlık kontrollerini yapar

# Renk tanımlamaları
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}OnlyVips Smoke Test başlatılıyor...${NC}"

# Değişkenler
RELEASE_NAME=${RELEASE_NAME:-"onlyvips"}
NAMESPACE=${NAMESPACE:-"default"}
BASE_API_URL=${BASE_API_URL:-"https://api.onlyvips.xyz"}
APP_URL=${APP_URL:-"https://app.onlyvips.xyz"}
PANEL_URL=${PANEL_URL:-"https://panel.onlyvips.xyz"}
TIMEOUT=10 # saniye cinsinden

# Test sonuçları
TESTS_PASSED=0
TESTS_FAILED=0
TEST_RESULTS=()

# Test fonksiyonu
run_test() {
    local name=$1
    local command=$2
    local expected_status=$3
    
    echo -e "${YELLOW}Test: $name${NC}"
    
    if eval "$command"; then
        if [ "$expected_status" = "success" ]; then
            echo -e "${GREEN}✓ Başarılı: $name${NC}"
            TESTS_PASSED=$((TESTS_PASSED + 1))
            TEST_RESULTS+=("✓ $name")
            return 0
        else
            echo -e "${RED}✗ Başarısız: $name - Başarılı olması beklenmeyen test başarılı oldu${NC}"
            TESTS_FAILED=$((TESTS_FAILED + 1))
            TEST_RESULTS+=("✗ $name - Unexpected success")
            return 1
        fi
    else
        if [ "$expected_status" = "failure" ]; then
            echo -e "${GREEN}✓ Başarılı: $name - Beklenen başarısızlık${NC}"
            TESTS_PASSED=$((TESTS_PASSED + 1))
            TEST_RESULTS+=("✓ $name - Expected failure")
            return 0
        else
            echo -e "${RED}✗ Başarısız: $name${NC}"
            TESTS_FAILED=$((TESTS_FAILED + 1))
            TEST_RESULTS+=("✗ $name")
            return 1
        fi
    fi
}

# Ortam kontrolü
if [ -n "$(command -v kubectl)" ]; then
    echo "Kubernetes ortamı tespit edildi"
    DEPLOYMENT_ENV="k8s"
elif [ -f "docker-config/docker-compose.yml" ]; then
    echo "Docker Compose ortamı tespit edildi"
    DEPLOYMENT_ENV="docker"
else
    echo -e "${RED}Deployment ortamı tanımlanamadı!${NC}"
    exit 1
fi

# Kubernetes servisleri sağlık kontrolü
if [ "$DEPLOYMENT_ENV" = "k8s" ]; then
    echo "Kubernetes servisleri kontrol ediliyor..."
    
    # Tüm pod'ların çalışır durumda olduğunu kontrol et
    run_test "Tüm pod'ların durumu Running olmalı" \
        "kubectl get pods -n ${NAMESPACE} -l app.kubernetes.io/instance=${RELEASE_NAME} -o jsonpath='{.items[*].status.phase}' | tr ' ' '\n' | grep -v Running | wc -l | grep -q '^0$'" \
        "success"
    
    # Backend API sağlık kontrolü
    run_test "Backend API sağlık kontrolü" \
        "kubectl exec -n ${NAMESPACE} \$(kubectl get pods -n ${NAMESPACE} -l app=${RELEASE_NAME}-backend -o jsonpath='{.items[0].metadata.name}') -- curl -s http://localhost:8000/health | grep -q 'status.*ok'" \
        "success"
    
    # Web uygulaması sağlık kontrolü
    run_test "MiniApp sağlık kontrolü" \
        "kubectl exec -n ${NAMESPACE} \$(kubectl get pods -n ${NAMESPACE} -l app=${RELEASE_NAME}-miniapp -o jsonpath='{.items[0].metadata.name}') -- curl -s http://localhost:80/health | grep -q 'ok'" \
        "success"
    
    # Showcu Panel sağlık kontrolü
    run_test "Showcu Panel sağlık kontrolü" \
        "kubectl exec -n ${NAMESPACE} \$(kubectl get pods -n ${NAMESPACE} -l app=${RELEASE_NAME}-showcu-panel -o jsonpath='{.items[0].metadata.name}') -- curl -s http://localhost:80/health | grep -q 'ok'" \
        "success"

# Docker Compose servisleri sağlık kontrolü
elif [ "$DEPLOYMENT_ENV" = "docker" ]; then
    echo "Docker servisleri kontrol ediliyor..."
    
    # Tüm servislerin çalışır durumda olduğunu kontrol et
    run_test "Tüm container'lar Up durumunda olmalı" \
        "cd docker-config && docker-compose ps | grep -v Up | grep -v 'Name' | wc -l | grep -q '^0$'" \
        "success"
    
    # Backend API sağlık kontrolü
    run_test "Backend API sağlık kontrolü" \
        "docker exec onlyvips-backend curl -s http://localhost:8000/health | grep -q 'status.*ok'" \
        "success"
    
    # Web uygulaması sağlık kontrolü (container dışından)
    run_test "MiniApp sağlık kontrolü" \
        "curl -s http://localhost:3000/health | grep -q 'ok'" \
        "success"
    
    # Showcu Panel sağlık kontrolü (container dışından)
    run_test "Showcu Panel sağlık kontrolü" \
        "curl -s http://localhost:3001/health | grep -q 'ok'" \
        "success"
fi

# Dış URL'ler üzerinden test
if command -v curl &> /dev/null; then
    # API erişim testi
    run_test "API dış erişim testi" \
        "curl -s --max-time ${TIMEOUT} ${BASE_API_URL}/health | grep -q 'status.*ok'" \
        "success"
    
    # MiniApp erişim testi
    run_test "MiniApp dış erişim testi" \
        "curl -s --max-time ${TIMEOUT} ${APP_URL} | grep -q '<title>'" \
        "success"
    
    # Showcu Panel erişim testi
    run_test "Showcu Panel dış erişim testi" \
        "curl -s --max-time ${TIMEOUT} ${PANEL_URL} | grep -q '<title>'" \
        "success"
    
    # API temel fonksiyonalite testi
    run_test "API kullanıcı listesi erişim testi" \
        "curl -s --max-time ${TIMEOUT} -H 'Authorization: Bearer \${TEST_API_TOKEN}' ${BASE_API_URL}/api/v1/users | grep -q 'users\|total'" \
        "success"
fi

# Test sonuçlarını göster
echo -e "\n${YELLOW}Test Sonuçları:${NC}"
echo "-----------------------------------"
for result in "${TEST_RESULTS[@]}"; do
    echo "$result"
done
echo "-----------------------------------"
echo -e "Toplam Testler: $((TESTS_PASSED + TESTS_FAILED)), ${GREEN}Başarılı: $TESTS_PASSED${NC}, ${RED}Başarısız: $TESTS_FAILED${NC}"

# Çıkış kodu belirle
if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}Tüm smoke testleri başarıyla tamamlandı!${NC}"
    exit 0
else
    echo -e "${RED}Bazı smoke testleri başarısız oldu!${NC}"
    exit 1
fi 