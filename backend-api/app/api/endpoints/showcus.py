"""
Showcus (Content Creator) Management Endpoints
İçerik üretici yönetimi ve analitik
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, status, Query, Depends
from pydantic import BaseModel, EmailStr
import time
from datetime import datetime, timedelta

from app.utils.logger import app_logger
from app.utils.cache import UserCache, ContentCache, cached

router = APIRouter()

# Pydantic Models
class ShowcusProfile(BaseModel):
    id: str
    username: str
    display_name: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    cover_url: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None
    social_links: Dict[str, str] = {}
    categories: List[str] = []
    is_verified: bool = False
    is_premium: bool = False
    subscription_tier: str = "basic"  # basic, pro, premium
    created_at: str
    updated_at: str

class ShowcusStats(BaseModel):
    total_contents: int
    total_views: int
    total_likes: int
    total_downloads: int
    total_earnings: float
    followers_count: int
    premium_subscribers: int
    avg_rating: float
    content_by_type: Dict[str, int]
    monthly_views: List[Dict[str, Any]]
    top_contents: List[Dict[str, Any]]

class ShowcusEarnings(BaseModel):
    total_earnings: float
    this_month: float
    last_month: float
    pending_payout: float
    paid_out: float
    earnings_by_content: List[Dict[str, Any]]
    earnings_history: List[Dict[str, Any]]

class ShowcusSubscription(BaseModel):
    tier: str
    price: float
    features: List[str]
    subscriber_count: int
    monthly_revenue: float
    is_active: bool

class ShowcusUpdate(BaseModel):
    display_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    cover_url: Optional[str] = None
    phone: Optional[str] = None
    social_links: Optional[Dict[str, str]] = None
    categories: Optional[List[str]] = None

class ShowcusListResponse(BaseModel):
    showcus: List[ShowcusProfile]
    total: int
    page: int
    per_page: int
    has_next: bool

# Helper functions
async def get_current_user(request):
    """JWT middleware'den kullanıcı bilgilerini al"""
    if hasattr(request.state, 'current_user'):
        return request.state.current_user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required"
    )

def is_admin_user(user_data: dict) -> bool:
    """Kullanıcının admin olup olmadığını kontrol et"""
    return user_data.get("role") == "admin"

def generate_mock_stats(showcu_id: str) -> ShowcusStats:
    """Mock istatistik verisi oluştur"""
    return ShowcusStats(
        total_contents=45,
        total_views=12500,
        total_likes=890,
        total_downloads=234,
        total_earnings=1250.75,
        followers_count=567,
        premium_subscribers=89,
        avg_rating=4.7,
        content_by_type={
            "image": 25,
            "video": 15,
            "audio": 3,
            "document": 2
        },
        monthly_views=[
            {"month": "2024-01", "views": 3200},
            {"month": "2024-02", "views": 4100},
            {"month": "2024-03", "views": 5200}
        ],
        top_contents=[
            {"id": "content_1", "title": "Top Content 1", "views": 1200, "earnings": 45.50},
            {"id": "content_2", "title": "Top Content 2", "views": 980, "earnings": 38.20},
            {"id": "content_3", "title": "Top Content 3", "views": 756, "earnings": 29.80}
        ]
    )

# Endpoints
@router.get("/", response_model=ShowcusListResponse)
async def get_showcus_list(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    verified_only: bool = Query(False),
    premium_only: bool = Query(False),
    search: Optional[str] = Query(None)
):
    """
    İçerik üretici listesini getir
    """
    try:
        # Mock data
        mock_showcus = []
        for i in range(per_page):
            showcu_id = f"showcu_{i + ((page - 1) * per_page)}"
            mock_showcus.append(ShowcusProfile(
                id=showcu_id,
                username=f"creator{i + 1}",
                display_name=f"Content Creator {i + 1}",
                bio=f"Professional content creator specializing in {['photography', 'videography', 'art', 'music'][i % 4]}",
                avatar_url=f"https://cdn.onlyvips.com/avatars/{showcu_id}.jpg",
                cover_url=f"https://cdn.onlyvips.com/covers/{showcu_id}.jpg",
                email=f"creator{i + 1}@example.com",
                phone=f"+90555000{i:04d}",
                social_links={
                    "instagram": f"@creator{i + 1}",
                    "twitter": f"@creator{i + 1}",
                    "youtube": f"creator{i + 1}"
                },
                categories=["photography", "art"] if i % 2 == 0 else ["videography", "music"],
                is_verified=i % 3 == 0,
                is_premium=i % 4 == 0,
                subscription_tier=["basic", "pro", "premium"][i % 3],
                created_at="2024-01-01T00:00:00Z",
                updated_at="2024-01-01T00:00:00Z"
            ))
        
        return ShowcusListResponse(
            showcus=mock_showcus,
            total=150,  # Mock total
            page=page,
            per_page=per_page,
            has_next=page * per_page < 150
        )
        
    except Exception as e:
        app_logger.error(f"Get showcus list error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch showcus list"
        )

@router.get("/{showcu_id}", response_model=ShowcusProfile)
async def get_showcu_profile(showcu_id: str):
    """
    İçerik üretici profilini getir
    """
    try:
        # Cache'den kontrol et
        cached_profile = await UserCache.get_user(f"showcu_{showcu_id}")
        if cached_profile:
            return ShowcusProfile(**cached_profile)
        
        # Mock data
        if showcu_id.startswith("showcu_"):
            profile = ShowcusProfile(
                id=showcu_id,
                username="samplecreator",
                display_name="Sample Content Creator",
                bio="Professional photographer and videographer with 5+ years experience",
                avatar_url=f"https://cdn.onlyvips.com/avatars/{showcu_id}.jpg",
                cover_url=f"https://cdn.onlyvips.com/covers/{showcu_id}.jpg",
                email="creator@example.com",
                phone="+905551234567",
                social_links={
                    "instagram": "@samplecreator",
                    "twitter": "@samplecreator",
                    "youtube": "samplecreator"
                },
                categories=["photography", "videography"],
                is_verified=True,
                is_premium=True,
                subscription_tier="premium",
                created_at="2024-01-01T00:00:00Z",
                updated_at="2024-01-01T00:00:00Z"
            )
            
            # Cache'e kaydet
            await UserCache.set_user(f"showcu_{showcu_id}", profile.dict())
            return profile
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Showcu not found"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Get showcu profile error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch showcu profile"
        )

@router.get("/{showcu_id}/stats", response_model=ShowcusStats)
@cached(ttl=300, key_prefix="showcu_stats")
async def get_showcu_stats(showcu_id: str, request = None):
    """
    İçerik üretici istatistiklerini getir
    """
    try:
        # Kullanıcı doğrulama
        current_user = await get_current_user(request)
        
        # Yetki kontrolü (sadece kendi istatistiklerini veya admin görebilir)
        if current_user.get("user_id") != showcu_id and not is_admin_user(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view these stats"
            )
        
        # Mock istatistikler
        stats = generate_mock_stats(showcu_id)
        
        app_logger.info(f"Stats requested for showcu: {showcu_id}")
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Get showcu stats error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch showcu stats"
        )

@router.get("/{showcu_id}/earnings", response_model=ShowcusEarnings)
async def get_showcu_earnings(showcu_id: str, request = None):
    """
    İçerik üretici kazanç bilgilerini getir
    """
    try:
        # Kullanıcı doğrulama
        current_user = await get_current_user(request)
        
        # Yetki kontrolü (sadece kendi kazançlarını veya admin görebilir)
        if current_user.get("user_id") != showcu_id and not is_admin_user(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view earnings"
            )
        
        # Mock kazanç verileri
        earnings = ShowcusEarnings(
            total_earnings=2450.75,
            this_month=345.20,
            last_month=298.50,
            pending_payout=123.45,
            paid_out=2327.30,
            earnings_by_content=[
                {"content_id": "content_1", "title": "Top Content", "earnings": 89.50},
                {"content_id": "content_2", "title": "Popular Video", "earnings": 67.20},
                {"content_id": "content_3", "title": "Art Collection", "earnings": 45.80}
            ],
            earnings_history=[
                {"date": "2024-03-01", "amount": 345.20, "type": "content_sale"},
                {"date": "2024-02-28", "amount": 298.50, "type": "subscription"},
                {"date": "2024-02-15", "amount": 156.30, "type": "tip"}
            ]
        )
        
        app_logger.info(f"Earnings requested for showcu: {showcu_id}")
        return earnings
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Get showcu earnings error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch showcu earnings"
        )

@router.put("/{showcu_id}", response_model=ShowcusProfile)
async def update_showcu_profile(
    showcu_id: str,
    profile_update: ShowcusUpdate,
    request = None
):
    """
    İçerik üretici profilini güncelle
    """
    try:
        # Kullanıcı doğrulama
        current_user = await get_current_user(request)
        
        # Yetki kontrolü
        if current_user.get("user_id") != showcu_id and not is_admin_user(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this profile"
            )
        
        # Mevcut profili getir
        existing_profile = await UserCache.get_user(f"showcu_{showcu_id}")
        if not existing_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Showcu profile not found"
            )
        
        # Güncelleme verilerini uygula
        update_data = profile_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            existing_profile[field] = value
        
        existing_profile["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # Cache'i güncelle
        await UserCache.set_user(f"showcu_{showcu_id}", existing_profile)
        
        app_logger.info(f"Showcu profile updated: {showcu_id}")
        
        return ShowcusProfile(**existing_profile)
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Update showcu profile error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update showcu profile"
        )

@router.post("/{showcu_id}/verify")
async def verify_showcu(showcu_id: str, request = None):
    """
    İçerik üreticiyi doğrula (sadece admin)
    """
    try:
        # Kullanıcı doğrulama
        current_user = await get_current_user(request)
        
        # Admin kontrolü
        if not is_admin_user(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        # Profili getir ve güncelle
        existing_profile = await UserCache.get_user(f"showcu_{showcu_id}")
        if not existing_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Showcu profile not found"
            )
        
        existing_profile["is_verified"] = True
        existing_profile["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # Cache'i güncelle
        await UserCache.set_user(f"showcu_{showcu_id}", existing_profile)
        
        app_logger.info(f"Showcu verified: {showcu_id} by admin {current_user.get('user_id')}")
        
        return {"message": "Showcu verified successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Verify showcu error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify showcu"
        )

@router.post("/{showcu_id}/subscription")
async def create_subscription_plan(
    showcu_id: str,
    subscription_data: ShowcusSubscription,
    request = None
):
    """
    Abonelik planı oluştur
    """
    try:
        # Kullanıcı doğrulama
        current_user = await get_current_user(request)
        
        # Yetki kontrolü
        if current_user.get("user_id") != showcu_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to create subscription for this showcu"
            )
        
        # Abonelik planını kaydet (mock)
        subscription_id = f"sub_{showcu_id}_{int(time.time())}"
        
        app_logger.info(f"Subscription plan created: {subscription_id} for showcu {showcu_id}")
        
        return {
            "message": "Subscription plan created successfully",
            "subscription_id": subscription_id,
            "tier": subscription_data.tier,
            "price": subscription_data.price
        }
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Create subscription error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create subscription plan"
        )

@router.get("/{showcu_id}/contents")
async def get_showcu_contents(
    showcu_id: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    content_type: Optional[str] = Query(None)
):
    """
    İçerik üreticinin içeriklerini getir
    """
    try:
        # Mock içerik listesi
        mock_contents = []
        for i in range(per_page):
            content_id = f"content_{showcu_id}_{i}"
            mock_contents.append({
                "id": content_id,
                "title": f"Content {i + 1}",
                "type": content_type or "image",
                "views": 100 + i * 10,
                "likes": 10 + i,
                "earnings": 5.50 + i * 0.5,
                "created_at": "2024-01-01T00:00:00Z"
            })
        
        return {
            "contents": mock_contents,
            "total": 50,
            "page": page,
            "per_page": per_page,
            "has_next": page * per_page < 50
        }
        
    except Exception as e:
        app_logger.error(f"Get showcu contents error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch showcu contents"
        )

@router.post("/{showcu_id}/payout")
async def request_payout(showcu_id: str, amount: float, request = None):
    """
    Ödeme talebi oluştur
    """
    try:
        # Kullanıcı doğrulama
        current_user = await get_current_user(request)
        
        # Yetki kontrolü
        if current_user.get("user_id") != showcu_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to request payout for this showcu"
            )
        
        # Minimum ödeme tutarı kontrolü
        if amount < 50.0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Minimum payout amount is 50.00"
            )
        
        # Ödeme talebi oluştur (mock)
        payout_id = f"payout_{showcu_id}_{int(time.time())}"
        
        app_logger.info(f"Payout requested: {payout_id} for showcu {showcu_id}, amount: {amount}")
        
        return {
            "message": "Payout request created successfully",
            "payout_id": payout_id,
            "amount": amount,
            "status": "pending",
            "estimated_processing_time": "3-5 business days"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Request payout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to request payout"
        )
