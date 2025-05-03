#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OnlyVips Performans Testi - Locust Script
Bu script, OnlyVips platformunda mesaj işlemlerini test eder.
"""

import json
import random
import os
import time
from locust import HttpUser, task, between, events

# Test Yapılandırması
API_BASE_URL = "/api"
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Test Verileri
TEST_USERS = [
    {"telegramId": "123456789", "username": "test_user1"},
    {"telegramId": "987654321", "username": "test_user2"},
    {"telegramId": "555555555", "username": "test_user3"},
]

TEST_MESSAGES = [
    {"title": "Test Mesajı 1", "content": "Bu bir test mesajıdır."},
    {"title": "Önemli Duyuru", "content": "Sistem bakımda olacaktır."},
    {"title": "Kampanya", "content": "Yeni kullanıcılara özel fırsatlar."},
]

class UserBehavior(HttpUser):
    """Kullanıcı davranışlarını simüle eden Locust kullanıcı sınıfı"""
    
    # İstekler arasında 1-5 saniye bekle
    wait_time = between(1, 5)
    
    def on_start(self):
        """Her simülasyon başında kullanıcı girişi yap"""
        # Rastgele bir test kullanıcısı seç
        self.test_user = random.choice(TEST_USERS)
        
        # Login işlemi - JWT token al
        response = self.client.post(
            f"{API_BASE_URL}/auth/telegram",
            json={
                "telegramId": self.test_user["telegramId"],
                "username": self.test_user["username"],
                "firstName": "Test",
                "lastName": "User",
                "photoUrl": "https://example.com/photo.jpg"
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            self.token = result.get("token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.token = None
            self.headers = {}
            
        # Mesaj alıcıları listesi için kullanıcıları getir
        self.recipients = []
        try:
            response = self.client.get(
                f"{API_BASE_URL}/users", 
                headers=self.headers
            )
            if response.status_code == 200:
                users_data = response.json()
                if "users" in users_data:
                    self.recipients = [user["telegramId"] for user in users_data["users"]]
        except Exception:
            # Hata durumunda varsayılan alıcı listesi
            self.recipients = [user["telegramId"] for user in TEST_USERS]
    
    @task(3)
    def add_message(self):
        """Yeni mesaj ekleme testi - /add-message endpoint'i"""
        if not self.token:
            return
            
        # Rastgele mesaj oluştur
        message = random.choice(TEST_MESSAGES)
        recipient = random.choice(self.recipients) if self.recipients else "all"
        
        # Mesaj gönder
        start_time = time.time()
        
        response = self.client.post(
            f"{API_BASE_URL}/messages/add", 
            headers=self.headers,
            json={
                "title": message["title"],
                "content": message["content"],
                "recipientId": recipient,
                "messageType": "text"
            }
        )
        
        # Özel metrik kaydet
        duration = time.time() - start_time
        events.request.fire(
            request_type="POST",
            name="AddMessage",
            response_time=duration * 1000,  # milisaniye olarak
            response_length=len(response.content),
            response=response,
            context=None,
            exception=None
        )
    
    @task(5)
    def get_messages(self):
        """Mesaj listesi alma testi - /api/messages endpoint'i"""
        if not self.token:
            return
            
        # Mesajları getir
        start_time = time.time()
        
        response = self.client.get(
            f"{API_BASE_URL}/messages", 
            headers=self.headers
        )
        
        # Özel metrik kaydet
        duration = time.time() - start_time
        events.request.fire(
            request_type="GET",
            name="GetMessages",
            response_time=duration * 1000,  # milisaniye olarak
            response_length=len(response.content),
            response=response,
            context=None,
            exception=None
        )
    
    @task(2)
    def send_bot_message(self):
        """Bot üzerinden mesaj gönderme testi - send_message job"""
        if not self.token:
            return
            
        # Rastgele mesaj seç
        message = random.choice(TEST_MESSAGES)
        
        # Bot mesaj gönderme isteği
        start_time = time.time()
        
        response = self.client.post(
            f"{API_BASE_URL}/bot/send-message", 
            headers=self.headers,
            json={
                "userId": self.test_user["telegramId"],
                "message": message["content"],
                "is_urgent": random.choice([True, False])
            }
        )
        
        # Özel metrik kaydet
        duration = time.time() - start_time
        events.request.fire(
            request_type="POST",
            name="BotSendMessage",
            response_time=duration * 1000,  # milisaniye olarak
            response_length=len(response.content),
            response=response,
            context=None,
            exception=None
        )

# Locust çalıştırma komutu örneği:
# locust -f locust_test.py --host=http://localhost:8000 --users=100 --spawn-rate=10 