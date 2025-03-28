from datetime import datetime, timedelta
from app.models.interactions import Like, Visit
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import delete
from typing import Any, List, Optional
import uuid
import os
import shutil


from app.core.db import get_db
from app.core.security import get_current_user, get_current_verified_user
from app.core.config import settings
from app.models.user import User
from app.models.profile import Profile, Tag, Gender, SexualPreference, ProfilePicture
from app.schemas.profile import (
    DeleteAccountRequest,
    Profile as ProfileSchema,
    ProfileUpdate,
    ProfileTagUpdate,
    Tag as TagSchema,
    ProfilePicture as ProfilePictureSchema,
    LocationUpdate,
    PublicProfile,
    TagUpdateSchema
)
from app.services.profile import (
    get_profile_by_user_id,
    get_profile_by_username,
    is_profile_complete,
    update_profile,
    add_tag_to_profile,
    remove_tag_from_profile,
    update_profile_tags,
    add_profile_picture,
    remove_profile_picture,
    set_primary_picture,
    get_suggested_profiles,
    update_fame_rating
)
from app.services.interactions import visit_profile

router = APIRouter()

@router.get("/me", response_model=ProfileSchema)
async def get_my_profile(
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    # Use selectinload to eagerly load relationships
    query = (
        select(Profile)
        .options(
            selectinload(Profile.pictures),
            selectinload(Profile.tags)
        )
        .filter(Profile.user_id == current_user.id)
    )
    
    result = await db.execute(query)
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    return profile


@router.put("/me", response_model=ProfileSchema)
async def update_my_profile(
    profile_data: ProfileUpdate,
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    try:
        # Get profile with relationships
        stmt = select(Profile).options(
            selectinload(Profile.pictures),
            selectinload(Profile.tags)
        ).where(Profile.user_id == current_user.id)
        
        result = await db.execute(stmt)
        profile = result.scalar_one_or_none()

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )

        # Update profile fields
        for field, value in profile_data.dict(exclude_unset=True).items():
            setattr(profile, field, value)

        # Update is_complete status
        profile.is_complete = is_profile_complete(profile)
        
        # Save changes
        await db.commit()
        await db.refresh(profile)
        return profile

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/me/tags", response_model=ProfileSchema)
async def update_my_tags(
    tag_data: TagUpdateSchema,
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    query = (
        select(Profile)
        .options(
            selectinload(Profile.tags),
            selectinload(Profile.pictures)
        )
        .filter(Profile.user_id == current_user.id)
    )
    result = await db.execute(query)
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profil bulunamadı"
        )

    try:
        # Clear existing tags
        profile.tags = []
        
        # Add new tags
        for tag_name in tag_data.tags:
            # Check if tag already exists
            existing_tag_query = select(Tag).filter(Tag.name == tag_name)
            result = await db.execute(existing_tag_query)
            existing_tag = result.scalar_one_or_none()
            
            if existing_tag:
                # Use existing tag
                profile.tags.append(existing_tag)
            else:
                # Create new tag
                new_tag = Tag(name=tag_name)
                profile.tags.append(new_tag)
        
        await db.commit()
        await db.refresh(profile)
        
        return profile
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/me/location", response_model=ProfileSchema)
async def update_location(
    location: LocationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_verified_user)
):
    try:
        async with db.begin():
            # Get current profile with relationships loaded
            stmt = select(Profile).options(
                selectinload(Profile.pictures),
                selectinload(Profile.tags)
            ).where(Profile.user_id == current_user.id)
            
            result = await db.execute(stmt)
            profile = result.scalar_one_or_none()

            if not profile:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Profile not found"
                )

            # Update location
            profile.latitude = location.latitude
            profile.longitude = location.longitude
            
            await db.commit()
            
            # Return updated profile with relationships
            return profile

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/me/pictures", response_model=ProfilePictureSchema)
async def upload_profile_picture(
    is_primary: bool = Form(False),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Upload a profile picture
    """
    profile = await get_profile_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    # Validate file type
    allowed_extensions = [".jpg", ".jpeg", ".png", ".gif"]
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Dosya türü desteklenmiyor. Desteklenen türler: {', '.join(allowed_extensions)}"
        )
    
    # Create upload directory if it doesn't exist
    upload_dir = os.path.join(settings.MEDIA_ROOT, "profile_pictures", str(profile.id))
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(upload_dir, filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Normalize the file path for database storage
    relative_path = os.path.relpath(file_path, start=os.path.dirname(settings.MEDIA_ROOT))
    
    # Create backend URL
    backend_url = f"{settings.BACKEND_URL}/{relative_path.replace(os.sep, '/')}"
    
    # Add picture to profile
    picture = await add_profile_picture(db, profile.id, relative_path, backend_url, is_primary)
    if not picture:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum number of pictures reached (5)"
        )
    
    return picture

@router.put("/me/pictures/{picture_id}/primary", response_model=ProfilePictureSchema)
async def set_primary_profile_picture(
    picture_id: int,
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Set a profile picture as primary
    """
    try:
        # Get profile with relationships
        stmt = select(Profile).options(
            selectinload(Profile.pictures),
            selectinload(Profile.tags)
        ).where(Profile.user_id == current_user.id)
        
        result = await db.execute(stmt)
        profile = result.scalar_one_or_none()

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profil bulunamadı"
            )
        
        # Get picture
        picture_stmt = select(ProfilePicture).where(
            ProfilePicture.id == picture_id,
            ProfilePicture.profile_id == profile.id
        )
        result = await db.execute(picture_stmt)
        picture = result.scalar_one_or_none()

        if not picture:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resim bulunamadı"
            )
        
        # Set picture as primary
        await set_primary_picture(db, profile.id, picture.id)
        
        return picture

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/me/pictures/{picture_id}", response_model=dict)
async def delete_profile_picture(
    picture_id: int,
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Delete a profile picture
    """
    try:
        # Get profile with relationships
        stmt = select(Profile).options(
            selectinload(Profile.pictures),
            selectinload(Profile.tags)
        ).where(Profile.user_id == current_user.id)
        
        result = await db.execute(stmt)
        profile = result.scalar_one_or_none()

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        # Get picture
        picture_stmt = select(ProfilePicture).where(
            ProfilePicture.id == picture_id,
            ProfilePicture.profile_id == profile.id
        )
        result = await db.execute(picture_stmt)
        picture = result.scalar_one_or_none()

        if not picture:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Picture not found"
            )

        # Check if this is the primary picture
        was_primary = picture.is_primary

        # Remove picture from filesystem if it exists
        if os.path.exists(picture.file_path):
            os.remove(picture.file_path)

        # Remove picture from database
        await db.delete(picture)
        
        # If this was the primary picture and there are other pictures, set a new primary
        if was_primary and len(profile.pictures) > 1:
            remaining_pictures = [p for p in profile.pictures if p.id != picture_id]
            if remaining_pictures:
                remaining_pictures[0].is_primary = True
                db.add(remaining_pictures[0])

        # Update profile's is_complete status
        profile.is_complete = is_profile_complete(profile)
        db.add(profile)
        
        await db.commit()

        return {"message": "Resim başarıyla silindi"}

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/suggested", response_model=List[PublicProfile])
async def get_suggested(
    limit: int = 20,
    offset: int = 0,
    min_age: Optional[int] = None,
    max_age: Optional[int] = None,
    min_fame: Optional[float] = None,
    max_fame: Optional[float] = None,
    max_distance: Optional[float] = None,
        tags: Optional[List[str]] = Query(
        None, 
        description="List of tags to filter by",
        example=["music", "kitap"],  # Add example
        openapi_examples={
            "single_tag": {
                "summary": "Single tag filter",
                "value": ["music"]
            },
            "multiple_tags": {
                "summary": "Multiple tag filter",
                "value": ["music", "kitap", "spor"]
            }
        }
    ),
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get suggested profiles with age-based filtering
    """
    # Get user's profile
    profile = await get_profile_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profil bulunamadı"
        )
    
    # Check if profile is complete
    if not profile.is_complete:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lütfen profilinizi tamamlayın"
        )
    
    # Get suggested profiles with age filters
    suggested = await get_suggested_profiles(
        db=db,
        user_id=current_user.id,
        limit=limit,
        offset=offset,
        min_age=min_age,
        max_age=max_age,
        min_fame=min_fame,
        max_fame=max_fame,
        max_distance=max_distance,
        tags=tags
    )
    
    # Extract profiles
    profiles = []
    if not suggested:
        return profiles
    
    for item in suggested:
        profile_data = item["profile"]
        user_data = item["user"]
        
        # Combine profile and user data for public profile
        public_profile = PublicProfile(
            id=profile_data.id,
            username=user_data.username,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            gender=profile_data.gender,
            sexual_preference=profile_data.sexual_preference,
            biography=profile_data.biography,
            latitude=profile_data.latitude,
            longitude=profile_data.longitude,
            fame_rating=profile_data.fame_rating,
            is_online=user_data.is_online,
            last_online=user_data.last_online,
            pictures=profile_data.pictures,
            tags=profile_data.tags,
            birth_date=profile_data.birth_date
        )
        
        profiles.append(public_profile)
    
    return profiles


@router.get("/{username}", response_model=PublicProfile)
async def get_profile(
    username: str,
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get a profile by username
    """
    # Get user's profile
    user_profile = await get_profile_by_username(db, username)
    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    # Get requested profile with pictures and tags eagerly loaded
    result = await db.execute(
        select(Profile, User)
        .join(User, Profile.user_id == User.id)
        .options(selectinload(Profile.pictures), selectinload(Profile.tags))
        .filter(User.username == username)  # Use username filter to get correct profile
    )
    profile_data = result.first()
    
    if not profile_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    profile, user = profile_data
    
    # Record visit if not own profile - Only do this once
    if user.id != current_user.id:
        # Get current user's profile ID
        current_user_profile_result = await db.execute(
            select(Profile).filter(Profile.user_id == current_user.id)
        )
        current_user_profile = current_user_profile_result.scalar_one_or_none()
        
        if current_user_profile:
            # Check if a visit was already recorded recently (last 5 minutes)
            five_minutes_ago = datetime.utcnow() - timedelta(minutes=5)
            recent_visit_query = select(Visit).filter(
                Visit.visitor_id == current_user_profile.id,
                Visit.visited_id == profile.id,
                Visit.created_at > five_minutes_ago
            )
            
            recent_visit_result = await db.execute(recent_visit_query)
            recent_visit = recent_visit_result.scalar_one_or_none()
            
            # Only record a new visit if no recent visit exists
            if not recent_visit:
                await visit_profile(db, current_user_profile.id, profile.id)
    
    # Create public profile
    public_profile = PublicProfile(
        id=profile.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        gender=profile.gender,
        sexual_preference=profile.sexual_preference,
        biography=profile.biography,
        latitude=profile.latitude,
        longitude=profile.longitude,
        fame_rating=profile.fame_rating,
        is_online=user.is_online,
        last_online=user.last_online,
        pictures=profile.pictures,
        tags=profile.tags,
        birth_date=profile.birth_date
    )
    
    return public_profile

@router.get("/get-for-chat/{username}", response_model=PublicProfile)
async def get_profile(
    username: str,
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get a profile by username
    """
    # Get user's profile
    user_profile = await get_profile_by_username(db, username)
    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    # Get requested profile with pictures and tags eagerly loaded
    result = await db.execute(
        select(Profile, User)
        .join(User, Profile.user_id == User.id)
        .options(selectinload(Profile.pictures), selectinload(Profile.tags))
        .filter(User.username == username)  # Use username filter to get correct profile
    )
    profile_data = result.first()
    
    if not profile_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    profile, user = profile_data
    
    # Create public profile
    public_profile = PublicProfile(
        id=profile.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        gender=profile.gender,
        sexual_preference=profile.sexual_preference,
        biography=profile.biography,
        latitude=profile.latitude,
        longitude=profile.longitude,
        fame_rating=profile.fame_rating,
        is_online=user.is_online,
        last_online=user.last_online,
        pictures=profile.pictures,
        tags=profile.tags,
        birth_date=profile.birth_date
    )
    
    return public_profile

@router.get("/get-by-user_id/{user_id}", response_model=PublicProfile)
async def get_profile(
    user_id: str,
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get a profile by user_id
    """
    # Get user's profile
    user_profile = await get_profile_by_user_id(db, user_id)
    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    # Get requested profile with pictures and tags eagerly loaded
    result = await db.execute(
        select(Profile, User)
        .join(User, Profile.user_id == User.id)
        .options(selectinload(Profile.pictures), selectinload(Profile.tags))
        .filter(User.id == user_id)  # Use username filter to get correct profile
    )
    profile_data = result.first()

    if not profile_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    profile, user = profile_data

    # Create public profile
    public_profile = PublicProfile(
        id=profile.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        gender=profile.gender,
        sexual_preference=profile.sexual_preference,
        biography=profile.biography,
        latitude=profile.latitude,
        longitude=profile.longitude,
        fame_rating=profile.fame_rating,
        is_online=user.is_online,
        last_online=user.last_online,
        pictures=profile.pictures,
        tags=profile.tags,
        birth_date=profile.birth_date
    )
    
    return public_profile



@router.get("/check-real-profile/{username}", response_model=dict)
async def check_real_profile(
    username: str,
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Check if a profile is real
    """
    target_profile = await get_profile_by_username(db, username)
    if not target_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hedef profil bulunamadı"
        )
    
    # Sözlük olarak döndür, Boolean değer değil
    return {"exists": True}    
    
    

@router.put("/me/delete-account", response_model=dict)
async def delete_account(
    request: DeleteAccountRequest,
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Delete user account
    """
    try:
        # Get user profile
        profile = await get_profile_by_user_id(db, current_user.id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profil bulunamadı"
            )
        
        # Check password
        if not current_user.verify_password(request.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Hatalı şifre"
            )
        
        # Delete profile pictures
        for picture in profile.pictures:
            if os.path.exists(picture.file_path):
                os.remove(picture.file_path)
        
        # Delete profile
        await db.delete(profile)
        
        # Delete user
        await db.delete(current_user)
        
        await db.commit()
        
        return {"message": "Hesap başarıyla silindi"}

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/me/is-liked/{username}", response_model=dict)
async def check_if_liked(
    username: str,
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Check if current user has liked a profile
    """
    try:
        # Get target profile by username
        target_profile = await get_profile_by_username(db, username)
        if not target_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hedef profil bulunamadı"
            )
        
        # Get current user's profile
        current_profile = await get_profile_by_user_id(db, current_user.id)
        if not current_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profil bulunamadı"
            )
                
        stmt = select(Like).filter(
            Like.liker_id == current_profile.id,
            Like.liked_id == target_profile.id
        )
        
        result = await db.execute(stmt)
        like = result.scalar_one_or_none()
        
        return {"is_liked": like is not None}

    except Exception as e:
        import logging
        logging.error(f"Error in check_if_liked: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )