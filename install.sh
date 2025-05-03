#!/bin/bash

# Renk tanımları
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}OnlyVips${NC} monorepo kurulumu başlatılıyor..."

# Yarn kontrolü
if ! command -v yarn &> /dev/null; then
    echo -e "${GREEN}Yarn kuruluyor...${NC}"
    npm install -g yarn
else
    echo -e "${GREEN}Yarn zaten kurulu.${NC}"
fi

# Poetry kontrolü
if ! command -v poetry &> /dev/null; then
    echo -e "${GREEN}Poetry kuruluyor...${NC}"
    curl -sSL https://install.python-poetry.org | python3 -
    # PATH'e poetry'yi ekle
    export PATH="$HOME/.local/bin:$PATH"
else
    echo -e "${GREEN}Poetry zaten kurulu.${NC}"
fi

# Node paketlerini yükle
echo -e "${GREEN}Node paketleri yükleniyor...${NC}"
yarn install

# Python bağımlılıklarını yükle
echo -e "${GREEN}Python bağımlılıkları yükleniyor...${NC}"
poetry install

echo -e "${GREEN}Kurulum tamamlandı!${NC}"
echo -e "Aşağıdaki komutlarla servisleri başlatabilirsiniz:"
echo -e "${BLUE}Backend API:${NC} yarn start:backend"
echo -e "${BLUE}MiniApp:${NC} yarn start:miniapp"
echo -e "${BLUE}Şovcu Panel:${NC} yarn start:panel"
echo -e "${BLUE}Flirt-Bot:${NC} cd flirt-bot && poetry run python bot_listener.py" 