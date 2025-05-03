# OnlyVips Ortam Değişkenleri Örneği

Bu döküman, OnlyVips monorepo projesi için gerekli ortam değişkenlerini açıklar. Her servis için `.env` dosyası oluşturmak için bu değişkenleri kullanabilirsiniz.

## Projenin Kök Dizini İçin `.env` Örneği

```env
# MongoDB
MONGODB_URI=mongodb://root:rootpassword@localhost:27017/onlyvips?authSource=admin

# JWT Kimlik Doğrulama
JWT_SECRET=your_secret_key_change_this
JWT_EXPIRES_IN=30d

# API Yapılandırması
PORT=8000
NODE_ENV=development
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Telegram Bot
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_BOT_TOKEN=your_bot_token

# OpenAI
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-3.5-turbo

# TON Blockchain
TON_CENTER=https://toncenter.com/api/v2/jsonRPC
TON_API_KEY=your_ton_api_key
TON_WALLET_ADDRESS=your_ton_wallet_address

# Loglama
LOG_LEVEL=debug
```

## Backend API İçin `.env` Örneği

Backend API dizininde (`backend-api/.env`) şu değişkenleri kullanın:

```env
# MongoDB
MONGODB_URI=mongodb://root:rootpassword@localhost:27017/onlyvips?authSource=admin

# JWT
JWT_SECRET=your_secret_key_change_this
JWT_EXPIRES_IN=30d

# API Config
PORT=8000
NODE_ENV=development
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# TON Blockchain
TON_CENTER=https://toncenter.com/api/v2/jsonRPC
TON_API_KEY=your_ton_api_key
TON_WALLET_ADDRESS=your_ton_wallet_address

# Uploads
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=50mb
```

## Flirt-Bot İçin `.env` Örneği

Flirt-Bot dizininde (`flirt-bot/.env`) şu değişkenleri kullanın:

```env
# Telegram
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_BOT_TOKEN=your_bot_token
SESSION_STRING=optional_user_session

# Backend Connection
BACKEND_API_URL=http://localhost:8000

# OpenAI
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-3.5-turbo

# GPT Limits
GPT_MAX_USAGE_DAY=50
GPT_MAX_TOKENS=250

# Logging
LOG_LEVEL=debug
```

## MiniApp İçin `.env` Örneği

MiniApp dizininde (`miniapp/.env`) şu değişkenleri kullanın:

```env
VITE_API_URL=http://localhost:8000
VITE_TELEGRAM_BOT_USERNAME=YourBotUsername
VITE_TG_WEB_APP_VERSION=6.9
VITE_TON_NETWORK=testnet
```

## Şovcu Panel İçin `.env` Örneği

Şovcu Panel dizininde (`showcu-panel/.env`) şu değişkenleri kullanın:

```env
VITE_API_URL=http://localhost:8000
VITE_TON_NETWORK=testnet
VITE_TG_WEB_APP_VERSION=6.9
VITE_MEDIA_URL=http://localhost:8000/uploads
```

## Önemli Notlar

1. Gerçek ortam için tüm gizli değerleri benzersiz ve güvenli değerlerle değiştirin.
2. Üretim ortamında `NODE_ENV=production` olarak ayarlayın.
3. JWT secret değerinizi rastgele ve güçlü bir dize olarak belirleyin.
4. CORS_ORIGINS'i üretim alan adlarınıza göre güncelleyin.
5. Telegram API anahtarlarını https://my.telegram.org/apps adresinden alabilirsiniz.
6. Telegram bot token'ını Telegram'daki BotFather (@BotFather) üzerinden oluşturun.
7. OpenAI API anahtarını https://platform.openai.com/ adresinden alabilirsiniz.

## 📄 Lisans

© 2024 SiyahKare. Tüm hakları saklıdır. 