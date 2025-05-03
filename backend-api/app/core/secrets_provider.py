from abc import ABC, abstractmethod
import os
import logging
from enum import Enum
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class SecretBackendType(str, Enum):
    """Secret backend türleri"""
    ENV = "env"
    VAULT = "vault"
    AWS_SSM = "aws_ssm"

class SecretProvider(ABC):
    """Secret sağlayıcı temel sınıfı"""
    
    @abstractmethod
    def get_secret(self, key: str, default: Optional[Any] = None) -> Any:
        """Secret değerini almak için metod"""
        pass

class EnvSecretProvider(SecretProvider):
    """Ortam değişkenlerinden secrets okuyan provider"""
    
    def get_secret(self, key: str, default: Optional[Any] = None) -> Any:
        """Ortam değişkeninden secret değerini alır"""
        return os.getenv(key, default)

class VaultSecretProvider(SecretProvider):
    """HashiCorp Vault'tan secrets okuyan provider"""
    
    def __init__(self, vault_url: str, token: str, mount_point: str = "secret", path: str = "onlyvips"):
        """
        Args:
            vault_url: Vault sunucu URL'si
            token: Vault kimlik doğrulama token'ı
            mount_point: Vault secret engine mount point'i (default: "secret")
            path: Secret verilerinin bulunduğu yol (default: "onlyvips")
        """
        try:
            import hvac
            self.client = hvac.Client(url=vault_url, token=token)
            self.mount_point = mount_point
            self.path = path
            
            if not self.client.is_authenticated():
                logger.error("Vault bağlantısı kurulamadı: Kimlik doğrulama hatası")
                # Fallback to environment variables
                self.client = None
        except ImportError:
            logger.warning("hvac kütüphanesi yüklü değil. pip install hvac komutu ile yükleyin.")
            self.client = None
        except Exception as e:
            logger.error(f"Vault bağlantısı kurulurken hata oluştu: {str(e)}")
            self.client = None
    
    def get_secret(self, key: str, default: Optional[Any] = None) -> Any:
        """Vault'tan secret değerini alır"""
        if self.client is None:
            return os.getenv(key, default)
            
        try:
            # KV versiyonuna göre uygun metodu çağır
            try:
                # KV version 2
                secret_response = self.client.secrets.kv.v2.read_secret_version(
                    path=self.path,
                    mount_point=self.mount_point
                )
                secrets = secret_response["data"]["data"]
            except:
                # KV version 1
                secret_response = self.client.secrets.kv.v1.read_secret(
                    path=self.path,
                    mount_point=self.mount_point
                )
                secrets = secret_response["data"]
                
            return secrets.get(key, os.getenv(key, default))
        except Exception as e:
            logger.error(f"Vault'tan secret alınırken hata oluştu: {str(e)}")
            return os.getenv(key, default)

class AwsSsmSecretProvider(SecretProvider):
    """AWS SSM Parameter Store'dan secrets okuyan provider"""
    
    def __init__(self, prefix: str = "/onlyvips", region: Optional[str] = None):
        """
        Args:
            prefix: Parametre yolu öneki (default: "/onlyvips")
            region: AWS bölgesi (default: None - boto3 varsayılanları kullanır)
        """
        self.prefix = prefix
        self.region = region
        self._cache: Dict[str, Any] = {}
        
        try:
            import boto3
            self.ssm = boto3.client('ssm', region_name=region)
        except ImportError:
            logger.warning("boto3 kütüphanesi yüklü değil. pip install boto3 komutu ile yükleyin.")
            self.ssm = None
        except Exception as e:
            logger.error(f"AWS SSM bağlantısı kurulurken hata oluştu: {str(e)}")
            self.ssm = None
    
    def get_secret(self, key: str, default: Optional[Any] = None) -> Any:
        """AWS SSM Parameter Store'dan secret değerini alır"""
        if self.ssm is None:
            return os.getenv(key, default)
            
        # Önbellekte varsa oradan dön
        if key in self._cache:
            return self._cache[key]
            
        try:
            # Parametreyi oku
            parameter_path = f"{self.prefix}/{key}"
            response = self.ssm.get_parameter(
                Name=parameter_path,
                WithDecryption=True
            )
            value = response['Parameter']['Value']
            
            # Önbelleğe ekle
            self._cache[key] = value
            return value
        except Exception as e:
            logger.error(f"AWS SSM'den parametre alınırken hata oluştu: {str(e)}")
            return os.getenv(key, default)

def get_secret_provider(provider_type: str = None) -> SecretProvider:
    """Yapılandırmaya göre bir secret provider döndürür"""
    provider_type = provider_type or os.getenv("SECRET_PROVIDER", "env")
    
    if provider_type == SecretBackendType.VAULT:
        vault_url = os.getenv("VAULT_URL")
        vault_token = os.getenv("VAULT_TOKEN")
        
        if vault_url and vault_token:
            vault_mount = os.getenv("VAULT_MOUNT", "secret")
            vault_path = os.getenv("VAULT_PATH", "onlyvips")
            return VaultSecretProvider(
                vault_url=vault_url,
                token=vault_token,
                mount_point=vault_mount,
                path=vault_path
            )
        else:
            logger.warning("Vault URL veya token tanımlanmamış. Ortam değişkenleri kullanılacak.")
            return EnvSecretProvider()
            
    elif provider_type == SecretBackendType.AWS_SSM:
        prefix = os.getenv("SSM_PREFIX", "/onlyvips")
        region = os.getenv("AWS_REGION")
        return AwsSsmSecretProvider(prefix=prefix, region=region)
    
    return EnvSecretProvider() 