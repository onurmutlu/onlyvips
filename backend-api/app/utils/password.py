"""
Şifre Yardımcıları
Şifre hashleme ve doğrulama için fonksiyonlar
"""

import secrets
import hashlib
import base64
from typing import Tuple, Optional


def hash_password(password: str) -> Tuple[str, str]:
    """
    Güvenli şifre hash fonksiyonu
    İki string döndürür: salt ve hash
    """
    # Rastgele salt oluştur
    salt = secrets.token_hex(16)
    
    # Hash hesapla (sha256 + salt)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000  # Iterasyon sayısı
    )
    
    # Base64 formatında döndür
    hashed = base64.b64encode(password_hash).decode("utf-8")
    
    return salt, hashed


def verify_password(password: str, stored_salt: str, stored_hash: str) -> bool:
    """
    Şifre doğrulama fonksiyonu
    Verilen şifre ve kaydedilmiş salt/hash eşleşiyorsa True döndürür
    """
    # Aynı salt ile hash hesapla
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        stored_salt.encode("utf-8"),
        100000  # Iterasyon sayısı (kayıt sırasında kullanılanla aynı olmalı)
    )
    
    # Base64'e dönüştür
    hashed = base64.b64encode(password_hash).decode("utf-8")
    
    # Kaydedilmiş hash ile karşılaştır
    return hashed == stored_hash


def create_password_hash(password: str) -> str:
    """
    Şifre ve salt'ı birleştirip tek bir string olarak döndürür
    Format: {salt}${hash}
    """
    salt, hashed = hash_password(password)
    return f"{salt}${hashed}"


def verify_password_hash(password: str, password_hash: str) -> bool:
    """
    create_password_hash ile oluşturulan formatı kullanarak şifre doğrulama
    """
    try:
        salt, stored_hash = password_hash.split("$", 1)
        return verify_password(password, salt, stored_hash)
    except Exception:
        return False 