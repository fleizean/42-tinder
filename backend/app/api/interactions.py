from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, List, Dict

from app.core.db import get_db
from app.core.security import get_current_user, get_current_verified_user
from app.models.user import User
from app.schemas.interactions import LikeCreate, Like, Visit, BlockCreate, Block, ReportCreate, Report
from app.schemas.profile import PublicProfile
from app.services.profile import get_profile_by_user_id, get_profile_by_username
from app.services.interactions import (
    get_blocks_received,
    get_blocks_sent,
    is_blocked,
    like_profile,
    unlike_profile,
    block_profile,
    unblock_profile,
    report_profile,
    get_likes_received,
    get_visits_received,
    get_matches
)

router = APIRouter()


@router.post("/like", response_model=dict)
async def create_like(
    like_data: LikeCreate,
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Like a profile
    """
    # Get user's profile
    profile = await get_profile_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Your profile not found"
        )
    
    # Check if profile is complete
    if not profile.is_complete:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please complete your profile first"
        )
    
    # Check if user has profile pictures
    if not profile.pictures or len(profile.pictures) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You need to upload at least one profile picture to like other profiles"
        )
    
    # Like profile
    result = await like_profile(db, profile.id, like_data.liked_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not like profile. The profile may not exist or might be blocked."
        )
    
    return {
        "message": "Profile liked successfully",
        "is_match": result["is_match"]
    }


@router.delete("/like/{profile_id}", response_model=dict)
async def delete_like(
    profile_id: str,
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Unlike a profile
    """
    # Get user's profile
    profile = await get_profile_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Your profile not found"
        )
    
    # Unlike profile
    result = await unlike_profile(db, profile.id, profile_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not unlike profile. You might not have liked this profile."
        )
    
    return {
        "message": "Profile unliked successfully"
    }


@router.post("/block", response_model=dict)
async def create_block(
    block_data: BlockCreate,
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Block a profile by either blocked_id (profile_id) or blocked_user_id (user_id)
    """
    # Get user's profile
    profile = await get_profile_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profil bulunamadı"
        )
    
    # Determine blocked profile ID
    blocked_profile_id = None
    
    # If blocked_id is provided (profile_id)
    if block_data.blocked_id:
        blocked_profile_id = block_data.blocked_id
    # If blocked_user_id is provided, get the profile_id
    elif block_data.blocked_user_id:
        blocked_profile = await get_profile_by_user_id(db, block_data.blocked_user_id)
        if not blocked_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profil bulunamadı"
            )
        blocked_profile_id = blocked_profile.id
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profil ID veya kullanıcı ID'si sağlanmalıdır"
        )
    # Block profile
    result = await block_profile(db, profile.id, blocked_profile_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profil engellenemedi. Profil mevcut olmayabilir."
        )
    
    return {
        "message": "Profil başarıyla engellendi"
    }

@router.delete("/block/{profile_id}", response_model=dict)
async def delete_block(
    profile_id: str,
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Unblock a profile
    """
    # Get user's profile
    profile = await get_profile_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Your profile not found"
        )
    
    # Unblock profile
    result = await unblock_profile(db, profile.id, profile_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not unblock profile. You might not have blocked this profile."
        )
    
    return {
        "message": "Profile unblocked successfully"
    }

@router.get("/block", response_model=List[PublicProfile])
async def get_blocks(
    limit: int = 10,
    offset: int = 0,
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get profiles that current user blocked
    """
    profile = await get_profile_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Your profile not found"
        )
    
    blocks = await get_blocks_sent(db, profile.id, limit, offset)
    
    profiles = []
    for block_data in blocks:
        blocked_profile = block_data["profile"]
        blocked_user = block_data["user"]
        
        profiles.append(PublicProfile(
            id=blocked_profile.id,
            username=blocked_user.username,
            first_name=blocked_user.first_name,
            last_name=blocked_user.last_name,
            is_online=blocked_user.is_online,
            pictures=blocked_profile.pictures,
            fame_rating=blocked_profile.fame_rating
        ))
    
    return profiles

@router.post("/is_blocked", response_model=dict)
async def check_if_blocked(
    blocked_username: str,
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Check if a user is blocked and who initiated the block
    """
    # Get user's profile
    profile = await get_profile_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Your profile not found"
        )
    
    # Get blocked user
    blocked_user = await get_profile_by_username(db, blocked_username)
    if not blocked_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if blocked in both directions
    is_blocked_by_me = await is_blocked(db, profile.id, blocked_user.id)
    is_blocked_by_them = await is_blocked(db, blocked_user.id, profile.id)
    
    return {
        "is_blocked": is_blocked_by_me or is_blocked_by_them,
        "blocked_by_me": is_blocked_by_me,
        "blocked_by_them": is_blocked_by_them,
        "blocker_id": blocked_user.id if is_blocked_by_them else (profile.id if is_blocked_by_me else None)
    }


@router.post("/report", response_model=dict)
async def create_report(
    report_data: ReportCreate,
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Report a profile
    """
    # Get user's profile
    profile = await get_profile_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profiliniz bulunamadı"
        )
    
    # Report profile
    result = await report_profile(db, profile.id, report_data.reported_id, report_data.reason, report_data.description)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profil raporlanamadı. Profil mevcut olmayabilir."
        )
    
    return {
        "message": "Profil başarıyla raporlandı"
    }


@router.get("/likes", response_model=List[PublicProfile])
async def get_likes(
    limit: int = 10,
    offset: int = 0,
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get profiles that liked current user
    """
    # Get user's profile
    profile = await get_profile_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Your profile not found"
        )
    
    # Get likes
    likes = await get_likes_received(db, profile.id, limit, offset)
    
    # Convert to public profiles
    profiles = []
    for like_data in likes:
        like = like_data["like"]
        liker_profile = like_data["profile"]
        liker_user = like_data["user"]
        liker_pictures = like_data.get("pictures", [])  # Eagerly loaded pictures
        liker_tags = like_data.get("tags", [])          # Eagerly loaded tags
        
        profiles.append(PublicProfile(
            id=liker_profile.id,
            username=liker_user.username,
            first_name=liker_user.first_name,
            last_name=liker_user.last_name,
            gender=liker_profile.gender,
            sexual_preference=liker_profile.sexual_preference,
            biography=liker_profile.biography,
            latitude=liker_profile.latitude,
            longitude=liker_profile.longitude,
            fame_rating=liker_profile.fame_rating,
            is_online=liker_user.is_online,
            last_online=liker_user.last_online,
            pictures=liker_pictures,  # Eagerly loaded pictures
            tags=liker_tags,          # Eagerly loaded tags
            birth_date=liker_profile.birth_date if hasattr(liker_profile, 'birth_date') else None
        ))
    
    return profiles

@router.get("/visits", response_model=List[PublicProfile])
async def get_visits(
    username: str,
    limit: int = 10,
    offset: int = 0,
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get profiles that visited current user
    """
    # Get user's profile
    profile = await get_profile_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Your profile not found"
        )
    
    # Get the target profile by username
    username_profile = await get_profile_by_username(db, username)
    if not username_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile with username {username} not found"
        )
    
    # Check permission - only allow current user to see their own visits
    if username_profile.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own visits"
        )
    
    # Get visits - burada kullanıcının profilini ziyaret edenler alınıyor
    visits = await get_visits_received(db, username_profile.id, limit, offset)
    
    # Ziyaretçilerin profillerini oluştur
    profiles = []
    for visit_data in visits:
        visit = visit_data["visit"]
        visitor_profile = visit_data["profile"] 
        visitor_user = visit_data["user"]
        visitor_pictures = visit_data.get("pictures", [])  # Eagerly loaded pictures
        visitor_tags = visit_data.get("tags", [])          # Eagerly loaded tags
        
        profiles.append(PublicProfile(
            id=visitor_profile.id,
            username=visitor_user.username,
            first_name=visitor_user.first_name,
            last_name=visitor_user.last_name,
            gender=visitor_profile.gender,
            sexual_preference=visitor_profile.sexual_preference,
            biography=visitor_profile.biography,
            latitude=visitor_profile.latitude,
            longitude=visitor_profile.longitude,
            fame_rating=visitor_profile.fame_rating,
            is_online=visitor_user.is_online,
            last_online=visitor_user.last_online,
            pictures=visitor_pictures,  # Eagerly loaded pictures kullan
            tags=visitor_tags,          # Eagerly loaded tags kullan
            birth_date=visitor_profile.birth_date
        ))
    
    return profiles

@router.get("/matches", response_model=List[PublicProfile])
async def get_user_matches(
    limit: int = 10,
    offset: int = 0,
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get current user's matches (mutual likes)
    """
    # Get matches
    matches = await get_matches(db, current_user.id, limit, offset)
    
    # Convert to public profiles
    profiles = []
    for match_data in matches:
        matched_profile = match_data["profile"]
        matched_user = match_data["user"]
        
        profiles.append(PublicProfile(
            id=matched_profile.id,
            username=matched_user.username,
            first_name=matched_user.first_name,
            last_name=matched_user.last_name,
            gender=matched_profile.gender,
            sexual_preference=matched_profile.sexual_preference,
            biography=matched_profile.biography,
            latitude=matched_profile.latitude,
            longitude=matched_profile.longitude,
            fame_rating=matched_profile.fame_rating,
            is_online=matched_user.is_online,
            last_online=matched_user.last_online,
            pictures=matched_profile.pictures,
            tags=matched_profile.tags
        ))
    
    return profiles