FROM node:18-alpine AS builder

WORKDIR /app

# Önbellek verimliliği için önce package.json dosyalarını kopyala
COPY package*.json ./

# Bağımlılıkları yükle
RUN npm ci

# Kaynak kodu kopyala
COPY . .

# Uygulamayı derle
RUN npm run build

# Nginx ile çalışan üretim aşaması
FROM nginx:alpine AS production

# Nginx yapılandırmasını kopyala
COPY ./nginx.conf /etc/nginx/conf.d/default.conf

# Derlenen uygulamayı nginx dizinine kopyala
COPY --from=builder /app/dist /usr/share/nginx/html

# 80 portunu aç
EXPOSE 80

# Sağlık kontrolü ekle
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:80/ || exit 1

# Nginx'i başlat
CMD ["nginx", "-g", "daemon off;"] 