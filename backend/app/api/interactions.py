from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, List, Dict

from app.core.db import get_db
from app.core.security import get_current_user, get_current_verified_user
from app.models.user import User
from app.schemas.interactions import LikeCreate, Like, Visit, BlockCreate, Block, ReportCreate, Report
from app.schemas.profile import PublicProfile
from app.services.profile import get_profile_by_user_id
from app.services.interactions import (
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
    Block a profile
    """
    # Get user's profile
    profile = await get_profile_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Your profile not found"
        )
    
    # Block profile
    result = await block_profile(db, profile.id, block_data.blocked_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not block profile. The profile may not exist."
        )
    
    return {
        "message": "Profile blocked successfully"
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
            detail="Your profile not found"
        )
    
    # Report profile
    result = await report_profile(db, profile.id, report_data.reported_id, report_data.reason)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not report profile. The profile may not exist."
        )
    
    return {
        "message": "Profile reported successfully"
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
            pictures=liker_profile.pictures,
            tags=liker_profile.tags
        ))
    
    return profiles


@router.get("/visits", response_model=List[PublicProfile])
async def get_visits(
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
    
    # Get visits
    visits = await get_visits_received(db, profile.id, limit, offset)
    
    # Convert to public profiles
    profiles = []
    for visit_data in visits:
        visit = visit_data["visit"]
        visitor_profile = visit_data["profile"]
        visitor_user = visit_data["user"]
        
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
            pictures=visitor_profile.pictures,
            tags=visitor_profile.tags
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