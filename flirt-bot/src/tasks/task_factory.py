#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Görev Fabrikası
Farklı görev türlerini oluşturmak için fabrika deseni uygulayan sınıf.
"""

import logging
import random
import time
from typing import Dict, List, Any, Optional, Union

logger = logging.getLogger(__name__)

class TaskFactory:
    """Görev oluşturucu fabrika sınıfı."""
    
    def __init__(self, task_manager, task_templates=None):
        """
        TaskFactory yapıcısı
        
        Args:
            task_manager: Görev yönetici nesnesi
            task_templates (Dict, optional): Görev şablonları
        """
        self.task_manager = task_manager
        # Varsayılan görev şablonları veya kullanıcı tarafından verilenler
        self.task_templates = task_templates or self._get_default_templates()
        
    def _get_default_templates(self) -> Dict[str, Any]:
        """Varsayılan görev şablonlarını döndürür"""
        return {
            # Bot etiketleme görevleri
            "mention": {
                "type": "mention",
                "title": "Bot Etiketleme",
                "description": "Bir grupta botu etiketle",
                "difficulty": "easy",
                "reward": {
                    "xp": 5,
                    "star": 1
                },
                "templates": [
                    {
                        "params": {
                            "target_group": None,  # Herhangi bir grup
                            "min_mentions": 1
                        },
                        "message": "Herhangi bir grupta botu bir kez etiketle."
                    },
                    {
                        "params": {
                            "target_group": "onlyvips_chat",
                            "min_mentions": 1
                        },
                        "message": "@onlyvips_chat grubunda botu etiketle."
                    },
                    {
                        "params": {
                            "target_group": None,
                            "min_mentions": 3
                        },
                        "message": "Herhangi bir grupta botu 3 kez etiketle."
                    }
                ]
            },
            
            # Mesaj gönderme görevleri
            "message": {
                "type": "message",
                "title": "Mesaj Gönderme",
                "description": "Bota özel bir mesaj gönder",
                "difficulty": "easy",
                "reward": {
                    "xp": 3,
                    "star": 1
                },
                "templates": [
                    {
                        "params": {
                            "required_content": ["merhaba"],
                            "min_length": 5
                        },
                        "message": "Bota 'merhaba' içeren bir mesaj gönder."
                    },
                    {
                        "params": {
                            "required_content": ["görev", "tamamla"],
                            "min_length": 10
                        },
                        "message": "Bota hem 'görev' hem de 'tamamla' kelimelerini içeren bir mesaj gönder."
                    },
                    {
                        "params": {
                            "min_length": 20
                        },
                        "message": "Bota en az 20 karakter uzunluğunda bir mesaj gönder."
                    }
                ]
            },
            
            # Kanala katılma görevleri
            "channel_join": {
                "type": "channel_join",
                "title": "Kanala Katılma",
                "description": "Belirtilen kanala katıl",
                "difficulty": "easy",
                "reward": {
                    "xp": 8,
                    "star": 2
                },
                "templates": [
                    {
                        "params": {
                            "channel_username": "OnlyVipsChannel",
                            "min_duration": 0  # Anında doğrulama
                        },
                        "message": "@OnlyVipsChannel kanalına katıl."
                    },
                    {
                        "params": {
                            "channel_username": "OnlyVipsNews",
                            "min_duration": 3600  # 1 saat kalma
                        },
                        "message": "@OnlyVipsNews kanalına katıl ve en az 1 saat üye kal."
                    }
                ]
            },
            
            # Gruba katılma görevleri
            "group_join": {
                "type": "group_join",
                "title": "Gruba Katılma",
                "description": "Belirtilen gruba katıl",
                "difficulty": "easy",
                "reward": {
                    "xp": 10,
                    "star": 2
                },
                "templates": [
                    {
                        "params": {
                            "group_username": "OnlyVipsChat",
                            "min_duration": 0
                        },
                        "message": "@OnlyVipsChat grubuna katıl."
                    },
                    {
                        "params": {
                            "group_username": "OnlyVipsCommunity",
                            "min_duration": 86400  # 24 saat kalma
                        },
                        "message": "@OnlyVipsCommunity grubuna katıl ve en az 24 saat üye kal."
                    }
                ]
            },
            
            # Gönderi paylaşma görevleri
            "share": {
                "type": "share",
                "title": "Gönderi Paylaşma",
                "description": "Belirtilen gönderiyi paylaş",
                "difficulty": "medium",
                "reward": {
                    "xp": 15,
                    "star": 3
                },
                "templates": [
                    {
                        "params": {
                            "post_channel": "OnlyVipsChannel",
                            "post_id": None,  # Herhangi bir gönderi
                            "target_type": "any"
                        },
                        "message": "@OnlyVipsChannel kanalından herhangi bir gönderiyi paylaş."
                    },
                    {
                        "params": {
                            "post_channel": "OnlyVipsAnnounce",
                            "post_id": "123",  # Belirli bir gönderi
                            "target_type": "group"
                        },
                        "message": "@OnlyVipsAnnounce kanalından 123 ID'li gönderiyi bir grupta paylaş."
                    }
                ]
            },
            
            # Mesaj iletme görevleri
            "forward": {
                "type": "forward",
                "title": "Mesaj İletme",
                "description": "Belirtilen mesajı ilet",
                "difficulty": "medium",
                "reward": {
                    "xp": 12,
                    "star": 2
                },
                "templates": [
                    {
                        "params": {
                            "source_channel": "OnlyVipsAnnounce",
                            "message_id": "456",
                            "target_type": "any",
                            "min_forwards": 1
                        },
                        "message": "@OnlyVipsAnnounce kanalından 456 ID'li mesajı ilet."
                    },
                    {
                        "params": {
                            "source_channel": "OnlyVipsChannel",
                            "message_id": "789",
                            "target_type": "private",
                            "min_forwards": 3
                        },
                        "message": "@OnlyVipsChannel kanalından 789 ID'li mesajı en az 3 kişiye özel olarak ilet."
                    }
                ]
            },
            
            # Sabitleme görevleri
            "pin": {
                "type": "pin",
                "title": "Mesaj Sabitleme",
                "description": "Bir grupta mesaj sabitle",
                "difficulty": "hard",
                "reward": {
                    "xp": 20,
                    "star": 4,
                    "badge": "admin"
                },
                "templates": [
                    {
                        "params": {
                            "target_group": None,  # Herhangi bir grup
                            "require_admin": True
                        },
                        "message": "Yönetici olduğun herhangi bir grupta bir mesaj sabitle."
                    },
                    {
                        "params": {
                            "target_group": "OnlyVipsTest",
                            "require_admin": True
                        },
                        "message": "@OnlyVipsTest grubunda bir mesaj sabitle. (Not: Bu görev için grupta yönetici olmalısın)"
                    }
                ]
            },
            
            # Link paylaşma görevleri
            "link": {
                "type": "link",
                "title": "Link Paylaşma",
                "description": "Bot linkini bir yerde paylaş",
                "difficulty": "easy",
                "reward": {
                    "xp": 8,
                    "star": 2
                },
                "templates": [
                    {
                        "params": {
                            "domains": ["t.me/OnlyVipsBot"],
                            "target_group": None,
                            "require_custom_text": True
                        },
                        "message": "Bot linkini (t.me/OnlyVipsBot) açıklama metniyle birlikte herhangi bir yerde paylaş."
                    },
                    {
                        "params": {
                            "domains": ["onlyvips.com"],
                            "target_group": "OnlyVipsChat",
                            "require_custom_text": True
                        },
                        "message": "@OnlyVipsChat grubunda onlyvips.com sitesinin linkini açıklama metniyle paylaş."
                    }
                ]
            }
        }
    
    async def create_random_task(
        self, 
        user_id: str, 
        difficulty: str = None, 
        task_type: str = None, 
        duration_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Rastgele bir görev oluştur
        
        Args:
            user_id: Kullanıcı ID'si
            difficulty (optional): Zorluk seviyesi ('easy', 'medium', 'hard')
            task_type (optional): Belirli bir görev tipi
            duration_hours: Görev süresi (saat)
            
        Returns:
            Dict: Oluşturulan görev bilgileri
        """
        # Uygun şablonları filtrele
        available_templates = {}
        
        for template_key, template_data in self.task_templates.items():
            # Belirli bir görev tipi istenmiş mi?
            if task_type and template_data["type"] != task_type:
                continue
                
            # Belirli bir zorluk seviyesi istenmiş mi?
            if difficulty and template_data["difficulty"] != difficulty:
                continue
                
            # Uygun şablon
            available_templates[template_key] = template_data
        
        # Uygun şablon bulunamadı
        if not available_templates:
            logger.warning(f"Kriterlere uygun görev şablonu bulunamadı: type={task_type}, difficulty={difficulty}")
            return {"success": False, "error": "Uygun görev bulunamadı"}
        
        # Rastgele bir şablon seç
        template_key = random.choice(list(available_templates.keys()))
        template_data = available_templates[template_key]
        
        # Şablondan rastgele bir görev varyasyonu seç
        task_template = random.choice(template_data["templates"])
        
        # Görev parametrelerini hazırla
        task_params = task_template["params"]
        
        # Görevi ata
        task_id = await self.task_manager.assign_task(
            user_id=user_id,
            task_type=template_data["type"],
            task_params=task_params,
            duration_hours=duration_hours
        )
        
        if not task_id:
            return {"success": False, "error": "Görev oluşturulamadı"}
        
        # Başarılı sonucu döndür
        return {
            "success": True,
            "task_id": task_id,
            "task_type": template_data["type"],
            "title": template_data["title"],
            "description": task_template["message"],
            "difficulty": template_data["difficulty"],
            "reward": template_data["reward"],
            "expiry_time": int(time.time()) + (duration_hours * 3600)
        }
    
    async def create_specific_task(
        self, 
        user_id: str, 
        task_key: str, 
        template_index: int = 0, 
        duration_hours: int = 24,
        custom_params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Belirli bir görev oluştur
        
        Args:
            user_id: Kullanıcı ID'si
            task_key: Görev şablonu anahtarı
            template_index: Şablon varyasyonu indeksi
            duration_hours: Görev süresi (saat)
            custom_params: Özelleştirilmiş parametreler
            
        Returns:
            Dict: Oluşturulan görev bilgileri
        """
        # Şablonu bul
        template_data = self.task_templates.get(task_key)
        if not template_data:
            logger.warning(f"Görev şablonu bulunamadı: {task_key}")
            return {"success": False, "error": "Görev şablonu bulunamadı"}
        
        # Şablon varyasyonunu kontrol et
        if template_index >= len(template_data["templates"]):
            logger.warning(f"Geçersiz şablon indeksi: {template_index} >= {len(template_data['templates'])}")
            template_index = 0
        
        # Şablon varyasyonunu al
        task_template = template_data["templates"][template_index]
        
        # Görev parametrelerini hazırla
        task_params = dict(task_template["params"])
        
        # Özelleştirilmiş parametreleri ekle
        if custom_params:
            task_params.update(custom_params)
        
        # Görevi ata
        task_id = await self.task_manager.assign_task(
            user_id=user_id,
            task_type=template_data["type"],
            task_params=task_params,
            duration_hours=duration_hours
        )
        
        if not task_id:
            return {"success": False, "error": "Görev oluşturulamadı"}
        
        # Başarılı sonucu döndür
        return {
            "success": True,
            "task_id": task_id,
            "task_type": template_data["type"],
            "title": template_data["title"],
            "description": task_template["message"],
            "difficulty": template_data["difficulty"],
            "reward": template_data["reward"],
            "expiry_time": int(time.time()) + (duration_hours * 3600)
        }
    
    def get_available_task_types(self) -> List[Dict[str, Any]]:
        """
        Mevcut görev tiplerini listele
        
        Returns:
            List[Dict]: Görev tipleri listesi
        """
        result = []
        
        for key, template in self.task_templates.items():
            result.append({
                "key": key,
                "type": template["type"],
                "title": template["title"],
                "description": template["description"],
                "difficulty": template["difficulty"],
                "reward": template["reward"]
            })
        
        return result
    
    def get_task_template(self, task_key: str) -> Optional[Dict[str, Any]]:
        """
        Belirli bir görev şablonunu döndür
        
        Args:
            task_key: Görev şablonu anahtarı
            
        Returns:
            Dict or None: Görev şablonu veya None (bulunamadı)
        """
        return self.task_templates.get(task_key)
    
    def add_custom_template(self, task_key: str, template_data: Dict[str, Any]) -> bool:
        """
        Özel bir görev şablonu ekle
        
        Args:
            task_key: Görev şablonu anahtarı
            template_data: Şablon verileri
            
        Returns:
            bool: Başarılı ise True
        """
        try:
            # Şablon doğrulaması
            required_fields = ["type", "title", "description", "difficulty", "reward", "templates"]
            for field in required_fields:
                if field not in template_data:
                    logger.error(f"Geçersiz şablon: '{field}' alanı eksik")
                    return False
            
            # Var olan şablonu güncelle veya yeni ekle
            self.task_templates[task_key] = template_data
            logger.info(f"Özel görev şablonu eklendi: {task_key}")
            return True
            
        except Exception as e:
            logger.error(f"Özel şablon eklenirken hata: {e}")
            return False 