#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
NFT Utilities - NFT Yardımcı İşlevleri
Görev tamamlama sonrası rozet/NFT oluşturma ve yönetim işlevleri
"""

import os
import json
import time
import uuid
import logging
import aiohttp
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

class NFTManager:
    """NFT ve rozet oluşturma ve yönetim işlevlerini sağlar."""
    
    def __init__(self, storage_dir: str = "./data/nfts"):
        """
        NFTManager yapıcısı
        
        Args:
            storage_dir: NFT verilerinin saklanacağı dizin
        """
        self.storage_dir = storage_dir
        self.metadata_dir = os.path.join(storage_dir, "metadata")
        self.user_badges_dir = os.path.join(storage_dir, "user_badges")
        
        # Dizinleri oluştur
        os.makedirs(self.metadata_dir, exist_ok=True)
        os.makedirs(self.user_badges_dir, exist_ok=True)
        
        # Rozet şablonları
        self.badge_templates = {
            "channel_join_v2": {
                "name": "Kanal Katılımcısı",
                "description": "OnlyVips topluluğunun resmi kanalına katıldı",
                "image": "https://example.com/images/badges/channel_join.png",
                "attributes": [
                    {"trait_type": "Category", "value": "Community"},
                    {"trait_type": "Rarity", "value": "Common"}
                ]
            },
            "message_send": {
                "name": "Aktif Mesajlaşan",
                "description": "OnlyVips topluluğunda aktif olarak mesajlaştı",
                "image": "https://example.com/images/badges/message_send.png",
                "attributes": [
                    {"trait_type": "Category", "value": "Communication"},
                    {"trait_type": "Rarity", "value": "Common"}
                ]
            },
            "button_click": {
                "name": "Buton Dedektifi",
                "description": "OnlyVips botundaki etkileşimli butonları kullandı",
                "image": "https://example.com/images/badges/button_click.png",
                "attributes": [
                    {"trait_type": "Category", "value": "Interaction"},
                    {"trait_type": "Rarity", "value": "Common"}
                ]
            },
            "start_link": {
                "name": "Bağlantı Takipçisi",
                "description": "OnlyVips botunu özel start link ile başlattı",
                "image": "https://example.com/images/badges/start_link.png",
                "attributes": [
                    {"trait_type": "Category", "value": "Referral"},
                    {"trait_type": "Rarity", "value": "Rare"}
                ]
            },
            "voting": {
                "name": "Topluluk Oylayıcı",
                "description": "OnlyVips topluluğundaki ankete katıldı",
                "image": "https://example.com/images/badges/voting.png",
                "attributes": [
                    {"trait_type": "Category", "value": "Governance"},
                    {"trait_type": "Rarity", "value": "Uncommon"}
                ]
            },
            "schedule_post": {
                "name": "Zamanlı Paylaşımcı",
                "description": "OnlyVips topluluğunda planlanmış mesaj gönderdi",
                "image": "https://example.com/images/badges/schedule_post.png",
                "attributes": [
                    {"trait_type": "Category", "value": "Content Creation"},
                    {"trait_type": "Rarity", "value": "Rare"}
                ]
            },
            "comment": {
                "name": "Yorumcu",
                "description": "OnlyVips topluluğunda içeriklere yorum yaptı",
                "image": "https://example.com/images/badges/comment.png",
                "attributes": [
                    {"trait_type": "Category", "value": "Engagement"},
                    {"trait_type": "Rarity", "value": "Common"}
                ]
            },
            "follow_account": {
                "name": "Takipçi",
                "description": "OnlyVips topluluğunda hesapları takip etti",
                "image": "https://example.com/images/badges/follow.png",
                "attributes": [
                    {"trait_type": "Category", "value": "Networking"},
                    {"trait_type": "Rarity", "value": "Uncommon"}
                ]
            },
            "emoji_reaction": {
                "name": "Duygu İfadecisi",
                "description": "OnlyVips topluluğunda emoji tepkileri kullandı",
                "image": "https://example.com/images/badges/emoji.png",
                "attributes": [
                    {"trait_type": "Category", "value": "Engagement"},
                    {"trait_type": "Rarity", "value": "Common"}
                ]
            },
            "group_join_message": {
                "name": "Grup Katılımcısı",
                "description": "OnlyVips topluluğunun resmi grubuna katıldı ve mesaj gönderdi",
                "image": "https://example.com/images/badges/group_join.png",
                "attributes": [
                    {"trait_type": "Category", "value": "Community"},
                    {"trait_type": "Rarity", "value": "Uncommon"}
                ]
            }
        }
        
        logger.info(f"NFTManager başlatıldı: {storage_dir}")
    
    async def create_badge(
        self,
        user_id: str,
        task_id: str,
        task_type: str,
        completion_time: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Kullanıcıya görev tamamlama rozeti oluştur
        
        Args:
            user_id: Kullanıcı ID'si
            task_id: Görev ID'si
            task_type: Görev tipi
            completion_time: Tamamlanma zamanı (Unix timestamp)
            
        Returns:
            Dict: Rozet metadata'sı
        """
        try:
            # Tamamlanma zamanı belirtilmemişse şu anki zamanı kullan
            if not completion_time:
                completion_time = int(time.time())
                
            # Rozet ID'si oluştur
            badge_id = f"badge_{task_type}_{uuid.uuid4().hex[:8]}"
            
            # Şablon bilgilerini al
            template = self.badge_templates.get(task_type, {
                "name": f"{task_type.capitalize()} Rozeti",
                "description": f"OnlyVips platformunda {task_type} görevini tamamladı",
                "image": "https://example.com/images/badges/default.png",
                "attributes": [
                    {"trait_type": "Category", "value": "Task Completion"},
                    {"trait_type": "Rarity", "value": "Common"}
                ]
            })
            
            # Metadata oluştur
            metadata = {
                "badge_id": badge_id,
                "name": template["name"],
                "description": template["description"],
                "image": template["image"],
                "user_id": user_id,
                "task_id": task_id,
                "task_type": task_type,
                "completion_time": completion_time,
                "created_at": int(time.time()),
                "attributes": template["attributes"] + [
                    {"trait_type": "Completion Date", "value": datetime.fromtimestamp(completion_time).strftime("%Y-%m-%d")}
                ]
            }
            
            # Rozet metadata'sını kaydet
            metadata_path = os.path.join(self.metadata_dir, f"{badge_id}.json")
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
                
            # Kullanıcının rozetlerini güncelle
            await self._update_user_badges(user_id, badge_id)
            
            # Rozet ID'sini ve IPFS hash'ini döndür (mock)
            ipfs_hash = f"ipfs://Qm{uuid.uuid4().hex[:40]}"
            metadata["ipfs_hash"] = ipfs_hash
            
            logger.info(f"Rozet oluşturuldu: {badge_id} ({user_id}, {task_type})")
            return metadata
            
        except Exception as e:
            logger.error(f"Rozet oluşturulurken hata: {e}")
            return {
                "badge_id": f"error_{uuid.uuid4().hex[:8]}",
                "name": "Hata Rozeti",
                "description": "Rozet oluşturulurken bir hata oluştu",
                "error": str(e)
            }
    
    async def _update_user_badges(self, user_id: str, badge_id: str):
        """
        Kullanıcının rozet listesini güncelle
        
        Args:
            user_id: Kullanıcı ID'si
            badge_id: Rozet ID'si
        """
        try:
            # Kullanıcının rozet dosyasının yolunu belirle
            user_badges_path = os.path.join(self.user_badges_dir, f"{user_id}.json")
            
            # Mevcut rozetleri yükle veya yeni oluştur
            badges = []
            if os.path.exists(user_badges_path):
                with open(user_badges_path, "r", encoding="utf-8") as f:
                    badges = json.load(f)
            
            # Yeni rozeti ekle
            badges.append({
                "badge_id": badge_id,
                "awarded_at": int(time.time())
            })
            
            # Güncellenmiş rozet listesini kaydet
            with open(user_badges_path, "w", encoding="utf-8") as f:
                json.dump(badges, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Kullanıcı rozetleri güncellenirken hata: {e}")
    
    async def get_user_badges(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Kullanıcının rozetlerini getir
        
        Args:
            user_id: Kullanıcı ID'si
            
        Returns:
            List[Dict]: Kullanıcının rozetleri
        """
        try:
            # Kullanıcının rozet dosyasının yolunu belirle
            user_badges_path = os.path.join(self.user_badges_dir, f"{user_id}.json")
            
            # Rozet IDs'lerini yükle
            if not os.path.exists(user_badges_path):
                return []
                
            with open(user_badges_path, "r", encoding="utf-8") as f:
                badge_refs = json.load(f)
            
            # Her rozet için metadata'yı yükle
            badges = []
            for badge_ref in badge_refs:
                badge_id = badge_ref["badge_id"]
                metadata_path = os.path.join(self.metadata_dir, f"{badge_id}.json")
                
                if os.path.exists(metadata_path):
                    with open(metadata_path, "r", encoding="utf-8") as f:
                        metadata = json.load(f)
                        
                    badges.append({
                        "badge_id": badge_id,
                        "name": metadata.get("name", "Bilinmeyen Rozet"),
                        "description": metadata.get("description", ""),
                        "image": metadata.get("image", ""),
                        "task_type": metadata.get("task_type", ""),
                        "awarded_at": badge_ref.get("awarded_at", 0)
                    })
            
            # Kazanılma tarihine göre sırala (en yeni en üstte)
            badges.sort(key=lambda x: x["awarded_at"], reverse=True)
            
            return badges
            
        except Exception as e:
            logger.error(f"Kullanıcı rozetleri alınırken hata: {e}")
            return []
    
    async def get_badge_metadata(self, badge_id: str) -> Optional[Dict[str, Any]]:
        """
        Rozet metadata'sını getir
        
        Args:
            badge_id: Rozet ID'si
            
        Returns:
            Dict or None: Rozet metadata'sı veya None
        """
        try:
            metadata_path = os.path.join(self.metadata_dir, f"{badge_id}.json")
            
            if not os.path.exists(metadata_path):
                return None
                
            with open(metadata_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)
                
            return metadata
            
        except Exception as e:
            logger.error(f"Rozet metadata'sı alınırken hata: {e}")
            return None
    
    async def generate_mock_nft_transaction(
        self,
        user_id: str,
        badge_id: str,
        wallet_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Sahte NFT işlemi oluştur
        
        Args:
            user_id: Kullanıcı ID'si
            badge_id: Rozet ID'si
            wallet_address: Cüzdan adresi (belirtilmezse rastgele oluşturulur)
            
        Returns:
            Dict: NFT işlem bilgileri
        """
        try:
            # Rozet metadata'sını al
            metadata = await self.get_badge_metadata(badge_id)
            
            if not metadata:
                raise ValueError(f"Rozet bulunamadı: {badge_id}")
            
            # Cüzdan adresi belirtilmemişse rastgele oluştur
            if not wallet_address:
                wallet_address = f"0x{uuid.uuid4().hex[:40]}"
                
            # Sahte işlem hash'i oluştur
            tx_hash = f"0x{uuid.uuid4().hex}"
            
            # Sahte NFT işlemi oluştur
            transaction = {
                "tx_hash": tx_hash,
                "token_id": f"{int(time.time())}{badge_id[-4:]}",
                "contract_address": "0x1234567890abcdef1234567890abcdef12345678",
                "chain_id": 137,  # Polygon
                "chain_name": "Polygon",
                "wallet_address": wallet_address,
                "metadata_uri": metadata.get("ipfs_hash", f"ipfs://Qm{uuid.uuid4().hex[:40]}"),
                "name": metadata.get("name", "OnlyVips Badge"),
                "description": metadata.get("description", ""),
                "image": metadata.get("image", ""),
                "badge_id": badge_id,
                "user_id": user_id,
                "created_at": int(time.time()),
                "explorer_url": f"https://polygonscan.com/tx/{tx_hash}"
            }
            
            logger.info(f"Sahte NFT işlemi oluşturuldu: {tx_hash} ({user_id}, {badge_id})")
            return transaction
            
        except Exception as e:
            logger.error(f"Sahte NFT işlemi oluşturulurken hata: {e}")
            return {
                "error": str(e),
                "tx_hash": f"error_{uuid.uuid4().hex[:8]}",
                "status": "failed"
            } 