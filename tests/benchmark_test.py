#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OnlyVips Performans Benchmark Testleri
Bu module, OnlyVips'in kritik fonksiyonlarının performans ölçümlerini yapar.
"""

import os
import pytest
import time
import random
import string
import asyncio
import json
from datetime import datetime, timedelta
import pymongo
from pymongo import MongoClient
import sys
import requests

# Backend API için gerekli path eklemeleri
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend-api')))

# Test yapılandırması
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://root:onlyvipsdev@localhost:27017/onlyvips?authSource=admin")
API_URL = os.getenv("API_URL", "http://localhost:8000/api")

# Test verileri
TEST_USERS = [
    {"telegramId": f"test_{i}", "username": f"test_user_{i}"} for i in range(10)
]

# MongoDB bağlantısı
@pytest.fixture(scope="module")
def mongo_client():
    """MongoDB bağlantısı oluşturur"""
    client = MongoClient(MONGODB_URI)
    yield client
    client.close()

@pytest.fixture(scope="module")
def db(mongo_client):
    """Test veritabanını oluşturur ve döndürür"""
    # Test veritabanını kullan
    db = mongo_client.get_database()
    
    # Test koleksiyonları
    users_collection = db.users
    messages_collection = db.messages
    
    # Test kullanıcılarını oluştur
    for user in TEST_USERS:
        # Eğer kullanıcı yoksa ekle
        if not users_collection.find_one({"telegramId": user["telegramId"]}):
            users_collection.insert_one({
                "telegramId": user["telegramId"],
                "username": user["username"],
                "firstName": "Test",
                "lastName": "User",
                "profilePhoto": "https://example.com/photo.jpg",
                "isShowcu": False,
                "xp": 0,
                "badges": [],
                "stars": 0,
                "wallet": {"balance": 0},
                "completedTasks": [],
                "pendingTasks": [],
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow(),
            })
    
    yield db
    
    # Temizlik - Test verilerini sil
    # for user in TEST_USERS:
    #    users_collection.delete_one({"telegramId": user["telegramId"]})
    # messages_collection.delete_many({"test": True})

# Rastgele kullanıcı seç
@pytest.fixture
def random_user(db):
    """Mevcut test kullanıcılarından rastgele bir kullanıcı seçer"""
    users = list(db.users.find({"telegramId": {"$in": [u["telegramId"] for u in TEST_USERS]}}))
    if not users:
        pytest.skip("Test kullanıcısı bulunamadı")
    return random.choice(users)

# Rastgele mesaj oluştur
def generate_random_message():
    """Rastgele bir mesaj oluşturur"""
    return {
        "title": f"Test Message {''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}",
        "content": f"Bu bir test mesajıdır. {''.join(random.choices(string.ascii_letters + string.digits, k=50))}",
        "messageType": "text",
        "test": True,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow(),
    }

# Veritabanı Sorgu Benchmark Testleri
def test_db_user_lookup(benchmark, db, random_user):
    """Kullanıcı arama sorgusu benchmark testi"""
    
    def lookup_user():
        return db.users.find_one({"telegramId": random_user["telegramId"]})
    
    # Benchmark ölçümü
    result = benchmark(lookup_user)
    assert result is not None, "Kullanıcı bulunamadı"

def test_db_message_insert(benchmark, db, random_user):
    """Mesaj ekleme benchmark testi"""
    
    def insert_message():
        message = generate_random_message()
        message["senderId"] = random_user["telegramId"]
        message["recipientId"] = "all"
        result = db.messages.insert_one(message)
        return result.inserted_id
    
    # Benchmark ölçümü
    result = benchmark(insert_message)
    assert result is not None, "Mesaj eklenemedi"

def test_db_message_query(benchmark, db, random_user):
    """Mesaj sorgulama benchmark testi"""
    
    # Test için birkaç mesaj ekle
    for _ in range(5):
        message = generate_random_message()
        message["senderId"] = random_user["telegramId"]
        message["recipientId"] = "all"
        db.messages.insert_one(message)
    
    def query_messages():
        return list(db.messages.find(
            {"senderId": random_user["telegramId"], "test": True}
        ).sort("createdAt", -1).limit(10))
    
    # Benchmark ölçümü
    results = benchmark(query_messages)
    assert len(results) > 0, "Mesajlar bulunamadı"

def test_db_message_aggregate(benchmark, db):
    """Mesaj gruplama (aggregate) sorgusu benchmark testi"""
    
    def aggregate_messages():
        pipeline = [
            {"$match": {"test": True}},
            {"$group": {
                "_id": "$senderId",
                "count": {"$sum": 1},
                "latest": {"$max": "$createdAt"}
            }},
            {"$sort": {"latest": -1}},
            {"$limit": 10}
        ]
        return list(db.messages.aggregate(pipeline))
    
    # Benchmark ölçümü
    results = benchmark(aggregate_messages)
    assert isinstance(results, list), "Gruplama sorgusu başarısız"

# Mesaj Zamanlama (Scheduling) Testleri 
def test_message_scheduling_simulation(benchmark, db, random_user):
    """Mesaj zamanlama simülasyonu benchmark testi"""
    
    def schedule_messages():
        # Gerçek zamanlamayı simüle ediyoruz
        scheduled_time = datetime.utcnow() + timedelta(hours=1)
        
        # İş sırası koleksiyonunda saklayarak zamanlama yapıyoruz
        job = {
            "type": "send_message",
            "data": {
                "senderId": random_user["telegramId"],
                "recipientId": "all",
                "message": generate_random_message(),
                "scheduledAt": scheduled_time
            },
            "status": "pending",
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
            "test": True
        }
        
        result = db.jobs.insert_one(job)
        return result.inserted_id
    
    # Benchmark ölçümü
    result = benchmark(schedule_messages)
    assert result is not None, "Mesaj zamanlanamadı"

def test_scheduled_message_query(benchmark, db):
    """Zamanlanmış mesaj sorgulama benchmark testi"""
    
    def query_scheduled_messages():
        now = datetime.utcnow()
        
        # Şu an gönderilmesi gereken işleri bul
        pipeline = [
            {"$match": {
                "type": "send_message",
                "status": "pending",
                "data.scheduledAt": {"$lte": now},
                "test": True
            }},
            {"$sort": {"data.scheduledAt": 1}},
            {"$limit": 100}
        ]
        
        return list(db.jobs.aggregate(pipeline))
    
    # Benchmark ölçümü
    results = benchmark(query_scheduled_messages)
    assert isinstance(results, list), "Zamanlı mesaj sorgusu başarısız"

# API Endpoint Benchmark Testleri
def get_auth_token(user_id):
    """Test kullanıcısı için kimlik doğrulama token'ı alır"""
    try:
        response = requests.post(
            f"{API_URL}/auth/telegram",
            json={
                "telegramId": user_id,
                "username": f"user_{user_id}",
                "firstName": "Test",
                "lastName": "User"
            }
        )
        if response.status_code == 200:
            return response.json().get("token")
    except Exception as e:
        print(f"Token alınamadı: {e}")
    return None

def test_api_add_message(benchmark, random_user):
    """Mesaj ekleme API endpoint benchmark testi"""
    token = get_auth_token(random_user["telegramId"])
    if not token:
        pytest.skip("API token alınamadı")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    def add_message_api():
        message = generate_random_message()
        response = requests.post(
            f"{API_URL}/messages/add",
            headers=headers,
            json={
                "title": message["title"],
                "content": message["content"],
                "recipientId": "all",
                "messageType": "text",
                "test": True
            }
        )
        return response
    
    # Benchmark ölçümü
    response = benchmark(add_message_api)
    assert response.status_code in (200, 201), f"API isteği başarısız: {response.text}"

def test_api_get_messages(benchmark, random_user):
    """Mesaj listeleme API endpoint benchmark testi"""
    token = get_auth_token(random_user["telegramId"])
    if not token:
        pytest.skip("API token alınamadı")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    def get_messages_api():
        response = requests.get(
            f"{API_URL}/messages",
            headers=headers
        )
        return response
    
    # Benchmark ölçümü
    response = benchmark(get_messages_api)
    assert response.status_code == 200, f"API isteği başarısız: {response.text}"

def test_api_bot_send_message(benchmark, random_user):
    """Bot mesaj gönderme API endpoint benchmark testi"""
    token = get_auth_token(random_user["telegramId"])
    if not token:
        pytest.skip("API token alınamadı")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    def bot_send_message_api():
        message = generate_random_message()
        response = requests.post(
            f"{API_URL}/bot/send-message",
            headers=headers,
            json={
                "userId": random_user["telegramId"],
                "message": message["content"],
                "is_urgent": False,
                "test": True
            }
        )
        return response
    
    # Benchmark ölçümü
    response = benchmark(bot_send_message_api)
    assert response.status_code in (200, 201, 202), f"API isteği başarısız: {response.text}"

# Test çalıştırma komutu:
# pytest -xvs benchmark_test.py --benchmark-columns=min,max,mean,median,stddev 