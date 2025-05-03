#!/bin/bash
# OnlyVips Staging Deployment Script
# Bu script OnlyVips platformunu Kubernetes üzerinde staging ortamına yükler.

set -e

# Renkli çıktı için
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}OnlyVips Platform - Staging Deployment${NC}"
echo "-------------------------------------"

# Namespace kontrol et ve oluştur
if ! kubectl get namespace staging &> /dev/null; then
  echo -e "${YELLOW}Staging namespace oluşturuluyor...${NC}"
  kubectl create namespace staging
else
  echo -e "${GREEN}Staging namespace zaten mevcut.${NC}"
fi

# Gerekli Helm repo'ları ekle
echo -e "${YELLOW}Helm repo'ları ekleniyor...${NC}"
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Değerlerin dosyada olup olmadığını kontrol et
if [ ! -f "staging-values.yaml" ]; then
  echo -e "${RED}Hata: staging-values.yaml dosyası bulunamadı!${NC}"
  echo "Lütfen değerleri yapılandırmak için values.yaml dosyasından bir kopya oluşturun."
  exit 1
fi

# Secret değerlerinin olup olmadığını kontrol et
if [ ! -f "staging-secrets.yaml" ]; then
  echo -e "${YELLOW}Uyarı: staging-secrets.yaml dosyası bulunamadı!${NC}"
  echo "Secret değerleri için ayrı bir dosya oluşturmak ister misiniz? (e/h)"
  read -r CREATE_SECRETS
  
  if [[ $CREATE_SECRETS == "e" ]]; then
    cp values.yaml staging-secrets.yaml
    echo -e "${GREEN}staging-secrets.yaml dosyası oluşturuldu. Lütfen düzenleyip tekrar çalıştırın.${NC}"
    exit 0
  fi
fi

# Helm chart kurulumu
echo -e "${YELLOW}OnlyVips Chart Staging ortamına yükleniyor...${NC}"

HELM_ARGS="-f staging-values.yaml"

if [ -f "staging-secrets.yaml" ]; then
  HELM_ARGS="$HELM_ARGS -f staging-secrets.yaml"
fi

# Chart'ı kur veya yükselt
if helm status -n staging staging &> /dev/null; then
  echo -e "${YELLOW}Mevcut kurulum güncelleniyor...${NC}"
  helm upgrade staging ../onlyvips-chart/ --namespace staging $HELM_ARGS
else
  echo -e "${YELLOW}Yeni kurulum yapılıyor...${NC}"
  helm install staging ../onlyvips-chart/ --namespace staging $HELM_ARGS
fi

# Kurulum durumunu kontrol et
echo -e "${YELLOW}Kurulum tamamlandı. Pod'lar kontrol ediliyor...${NC}"
kubectl get pods -n staging

echo -e "${YELLOW}Servisleri kontrol et:${NC}"
kubectl get svc -n staging

echo -e "${YELLOW}Ingress'leri kontrol et:${NC}"
kubectl get ingress -n staging

echo -e "${GREEN}Deployment tamamlandı!${NC}"
echo "-------------------------------------"
echo -e "Uygulamayı test etmek için aşağıdaki adresleri kullanabilirsiniz:"

# Ingress'leri bul ve URLs göster
BACKEND_HOST=$(kubectl get ingress -n staging -l app=backend -o jsonpath='{.items[0].spec.rules[0].host}' 2>/dev/null || echo "backend URL bulunamadı")
MINIAPP_HOST=$(kubectl get ingress -n staging -l app=miniapp -o jsonpath='{.items[0].spec.rules[0].host}' 2>/dev/null || echo "miniapp URL bulunamadı")
SHOWCU_HOST=$(kubectl get ingress -n staging -l app=showcu-panel -o jsonpath='{.items[0].spec.rules[0].host}' 2>/dev/null || echo "showcu-panel URL bulunamadı")

echo -e "Backend API: ${GREEN}https://$BACKEND_HOST${NC}"
echo -e "MiniApp: ${GREEN}https://$MINIAPP_HOST${NC}"
echo -e "Showcu Panel: ${GREEN}https://$SHOWCU_HOST${NC}"

echo "-------------------------------------"
echo -e "${YELLOW}Logları görüntülemek için:${NC}"
echo "kubectl logs -n staging -l app=backend -f"
echo "kubectl logs -n staging -l app=flirt-bot -f" 