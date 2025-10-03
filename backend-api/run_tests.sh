#!/bin/bash

# OnlyVips Backend API Test Runner
# Test coverage ve raporlama ile birlikte testleri çalıştırır

echo "🧪 OnlyVips Backend API Test Suite"
echo "=================================="

# Virtual environment kontrolü
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Virtual environment aktif değil!"
    echo "Lütfen önce virtual environment'ı aktifleştirin:"
    echo "source venv/bin/activate"
    exit 1
fi

# Test dependencies kontrolü
echo "📦 Test bağımlılıklarını kontrol ediliyor..."
pip install -q pytest pytest-asyncio pytest-cov httpx

# Test environment ayarları
export ENVIRONMENT=test
export DB_PROVIDER=memory
export REDIS_HOST=localhost
export LOG_LEVEL=WARNING

echo "🔧 Test ortamı hazırlanıyor..."

# Test klasörü kontrolü
if [ ! -d "tests" ]; then
    echo "❌ Test klasörü bulunamadı!"
    exit 1
fi

# Testleri çalıştır
echo "🚀 Testler çalıştırılıyor..."

# Unit testler
echo "📋 Unit testler..."
pytest tests/ -v --tb=short --cov=app --cov-report=term-missing --cov-report=html:htmlcov

# Test sonuçları
TEST_EXIT_CODE=$?

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ Tüm testler başarılı!"
    echo "📊 Coverage raporu: htmlcov/index.html"
else
    echo "❌ Bazı testler başarısız!"
    exit $TEST_EXIT_CODE
fi

# Coverage threshold kontrolü
echo "📈 Coverage threshold kontrolü..."
coverage report --fail-under=80

if [ $? -eq 0 ]; then
    echo "✅ Coverage threshold (%80) karşılandı!"
else
    echo "⚠️  Coverage threshold (%80) karşılanmadı!"
    echo "Lütfen daha fazla test yazın."
fi

echo "🎉 Test suite tamamlandı!" 