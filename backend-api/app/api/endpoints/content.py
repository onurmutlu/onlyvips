"""
Content Management Endpoints
İçerik yönetimi ve medya işlemleri
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Query
from pydantic import BaseModel
import time
import hashlib
import os

from app.utils.logger import app_logger
from app.utils.cache import ContentCache, cache_invalidate
from app.middleware.jwt_security import JWTSecurityMiddleware

router = APIRouter()

# Pydantic Models
class ContentBase(BaseModel):
    title: str
    description: Optional[str] = None
    type: str  # image, video, audio, document
    category: Optional[str] = None
    tags: List[str] = []
    is_premium: bool = False
    price: Optional[float] = None
    access_requirements: Optional[dict] = None

class ContentCreate(ContentBase):
    pass

class ContentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    is_premium: Optional[bool] = None
    price: Optional[float] = None
    access_requirements: Optional[dict] = None

class ContentResponse(ContentBase):
    id: str
    creator_id: str
    creator_username: str
    url: str
    thumbnail_url: Optional[str] = None
    file_size: Optional[int] = None
    duration: Optional[int] = None  # For video/audio
    views: int = 0
    likes: int = 0
    downloads: int = 0
    created_at: str
    updated_at: str

class ContentListResponse(BaseModel):
    contents: List[ContentResponse]
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

def generate_file_hash(file_content: bytes) -> str:
    """Dosya hash'i oluştur"""
    return hashlib.sha256(file_content).hexdigest()

def get_file_extension(filename: str) -> str:
    """Dosya uzantısını al"""
    return os.path.splitext(filename)[1].lower()

def validate_file_type(file_type: str, allowed_types: List[str]) -> bool:
    """Dosya tipini doğrula"""
    return file_type in allowed_types

# Endpoints
@router.get("/", response_model=ContentListResponse)
async def get_contents(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    content_type: Optional[str] = Query(None),
    creator_id: Optional[str] = Query(None),
    is_premium: Optional[bool] = Query(None),
    search: Optional[str] = Query(None)
):
    """
    İçerik listesini getir
    """
    try:
        # Cache key oluştur
        filters = f"page:{page},per_page:{per_page},category:{category},type:{content_type},creator:{creator_id},premium:{is_premium},search:{search}"
        
        # Cache'den kontrol et
        cached_result = await ContentCache.get_content_list(filters)
        if cached_result:
            return cached_result
        
        # Mock data (gerçek implementasyonda database'den gelecek)
        mock_contents = []
        for i in range(per_page):
            content_id = f"content_{i + ((page - 1) * per_page)}"
            mock_contents.append(ContentResponse(
                id=content_id,
                title=f"Test Content {i + 1}",
                description=f"Description for content {i + 1}",
                type="image",
                category="general",
                tags=["test", "demo"],
                is_premium=i % 3 == 0,
                price=10.0 if i % 3 == 0 else None,
                creator_id="creator_123",
                creator_username="testcreator",
                url=f"https://example.com/content/{content_id}",
                thumbnail_url=f"https://example.com/thumbnails/{content_id}",
                file_size=1024 * 1024,  # 1MB
                views=100 + i,
                likes=10 + i,
                downloads=5 + i,
                created_at="2024-01-01T00:00:00Z",
                updated_at="2024-01-01T00:00:00Z"
            ))
        
        result = ContentListResponse(
            contents=mock_contents,
            total=100,  # Mock total
            page=page,
            per_page=per_page,
            has_next=page * per_page < 100
        )
        
        # Cache'e kaydet
        await ContentCache.set_content_list(filters, result.dict(), ttl=600)
        
        return result
        
    except Exception as e:
        app_logger.error(f"Content list error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch contents"
        )

@router.get("/{content_id}", response_model=ContentResponse)
async def get_content(content_id: str):
    """
    Belirli bir içeriği getir
    """
    try:
        # Cache'den kontrol et
        cached_content = await ContentCache.get_content(content_id)
        if cached_content:
            return ContentResponse(**cached_content)
        
        # Mock data (gerçek implementasyonda database'den gelecek)
        if content_id.startswith("content_"):
            content = ContentResponse(
                id=content_id,
                title="Sample Content",
                description="This is a sample content",
                type="image",
                category="general",
                tags=["sample", "test"],
                is_premium=False,
                creator_id="creator_123",
                creator_username="testcreator",
                url=f"https://example.com/content/{content_id}",
                thumbnail_url=f"https://example.com/thumbnails/{content_id}",
                file_size=1024 * 1024,
                views=150,
                likes=25,
                downloads=10,
                created_at="2024-01-01T00:00:00Z",
                updated_at="2024-01-01T00:00:00Z"
            )
            
            # Cache'e kaydet
            await ContentCache.set_content(content_id, content.dict())
            return content
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Get content error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch content"
        )

@router.post("/upload", response_model=ContentResponse)
async def upload_content(
    file: UploadFile = File(...),
    title: str = Query(...),
    description: Optional[str] = Query(None),
    category: Optional[str] = Query("general"),
    is_premium: bool = Query(False),
    price: Optional[float] = Query(None),
    request = None
):
    """
    Yeni içerik yükle
    """
    try:
        # Kullanıcı doğrulama
        current_user = await get_current_user(request)
        
        # Dosya boyutu kontrolü (max 50MB)
        max_size = 50 * 1024 * 1024  # 50MB
        file_content = await file.read()
        
        if len(file_content) > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File size exceeds 50MB limit"
            )
        
        # Dosya tipi kontrolü
        allowed_types = ['.jpg', '.jpeg', '.png', '.gif', '.mp4', '.mov', '.mp3', '.wav', '.pdf', '.doc', '.docx']
        file_ext = get_file_extension(file.filename)
        
        if file_ext not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {file_ext} not allowed"
            )
        
        # Dosya hash'i oluştur
        file_hash = generate_file_hash(file_content)
        content_id = f"content_{file_hash[:16]}"
        
        # Dosya tipini belirle
        content_type = "image"
        if file_ext in ['.mp4', '.mov']:
            content_type = "video"
        elif file_ext in ['.mp3', '.wav']:
            content_type = "audio"
        elif file_ext in ['.pdf', '.doc', '.docx']:
            content_type = "document"
        
        # Mock file upload (gerçek implementasyonda S3/CDN'e yüklenecek)
        file_url = f"https://cdn.onlyvips.com/content/{content_id}{file_ext}"
        thumbnail_url = f"https://cdn.onlyvips.com/thumbnails/{content_id}.jpg"
        
        # İçerik oluştur
        content = ContentResponse(
            id=content_id,
            title=title,
            description=description,
            type=content_type,
            category=category,
            tags=[],
            is_premium=is_premium,
            price=price if is_premium else None,
            creator_id=current_user.get("user_id"),
            creator_username=current_user.get("username"),
            url=file_url,
            thumbnail_url=thumbnail_url,
            file_size=len(file_content),
            views=0,
            likes=0,
            downloads=0,
            created_at=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            updated_at=time.strftime("%Y-%m-%dT%H:%M:%SZ")
        )
        
        # Cache'e kaydet
        await ContentCache.set_content(content_id, content.dict())
        
        # Content list cache'ini temizle
        await cache_invalidate("content_list:*")
        
        app_logger.info(f"Content uploaded: {content_id} by user {current_user.get('user_id')}")
        
        return content
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Upload content error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload content"
        )

@router.put("/{content_id}", response_model=ContentResponse)
async def update_content(
    content_id: str,
    content_update: ContentUpdate,
    request = None
):
    """
    İçeriği güncelle
    """
    try:
        # Kullanıcı doğrulama
        current_user = await get_current_user(request)
        
        # Mevcut içeriği getir
        existing_content = await ContentCache.get_content(content_id)
        if not existing_content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found"
            )
        
        # Yetki kontrolü
        if existing_content["creator_id"] != current_user.get("user_id"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this content"
            )
        
        # Güncelleme verilerini uygula
        update_data = content_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            existing_content[field] = value
        
        existing_content["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # Cache'i güncelle
        await ContentCache.set_content(content_id, existing_content)
        
        # Content list cache'ini temizle
        await cache_invalidate("content_list:*")
        
        app_logger.info(f"Content updated: {content_id} by user {current_user.get('user_id')}")
        
        return ContentResponse(**existing_content)
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Update content error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update content"
        )

@router.delete("/{content_id}")
async def delete_content(content_id: str, request = None):
    """
    İçeriği sil
    """
    try:
        # Kullanıcı doğrulama
        current_user = await get_current_user(request)
        
        # Mevcut içeriği getir
        existing_content = await ContentCache.get_content(content_id)
        if not existing_content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found"
            )
        
        # Yetki kontrolü
        if existing_content["creator_id"] != current_user.get("user_id"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this content"
            )
        
        # Cache'den sil
        await ContentCache.delete(f"content:{content_id}")
        
        # Content list cache'ini temizle
        await cache_invalidate("content_list:*")
        
        app_logger.info(f"Content deleted: {content_id} by user {current_user.get('user_id')}")
        
        return {"message": "Content deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Delete content error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete content"
        )

@router.post("/{content_id}/like")
async def like_content(content_id: str, request = None):
    """
    İçeriği beğen
    """
    try:
        # Kullanıcı doğrulama
        current_user = await get_current_user(request)
        
        # İçeriği getir
        content = await ContentCache.get_content(content_id)
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found"
            )
        
        # Like sayısını artır (gerçek implementasyonda user-content like tablosu kontrol edilecek)
        content["likes"] += 1
        
        # Cache'i güncelle
        await ContentCache.set_content(content_id, content)
        
        app_logger.info(f"Content liked: {content_id} by user {current_user.get('user_id')}")
        
        return {"message": "Content liked", "likes": content["likes"]}
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Like content error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to like content"
        )

@router.post("/{content_id}/view")
async def view_content(content_id: str):
    """
    İçerik görüntüleme sayısını artır
    """
    try:
        # İçeriği getir
        content = await ContentCache.get_content(content_id)
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found"
            )
        
        # View sayısını artır
        content["views"] += 1
        
        # Cache'i güncelle
        await ContentCache.set_content(content_id, content)
        
        return {"message": "View recorded", "views": content["views"]}
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"View content error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record view"
        )
