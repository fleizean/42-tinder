from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query, Request
from fastapi.responses import JSONResponse
from typing import Any, Dict, List, Optional
import uuid
import os
import shutil
from pathlib import Path

from app.core.db import get_connection
from app.core.security import get_current_user, get_current_verified_user
from app.core.config import settings
from app.validation.profile import validate_profile_update, validate_tags, validate_birth_date
from app.db import profiles as profiles_db

router = APIRouter()

@router.get("/me")
async def get_my_profile(
    current_user = Depends(get_current_verified_user),
    conn = Depends(get_connection)
):
    """Get current user's profile"""
    # Get profile
    profile = await conn.fetchrow("""
    SELECT * FROM profiles
    WHERE user_id = $1
    """, current_user["id"])
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    # Get profile pictures
    pictures = await conn.fetch("""
    SELECT id, profile_id, file_path, backend_url, is_primary, created_at
    FROM profile_pictures
    WHERE profile_id = $1
    ORDER BY is_primary DESC, created_at ASC
    """, profile["id"])
    
    # Get profile tags
    tags = await conn.fetch("""
    SELECT t.id, t.name
    FROM tags t
    JOIN profile_tags pt ON t.id = pt.tag_id
    WHERE pt.profile_id = $1
    """, profile["id"])
    
    # Combine data
    result = dict(profile)
    result["pictures"] = [dict(pic) for pic in pictures]
    result["tags"] = [dict(tag) for tag in tags]
    
    return result

@router.put("/me")
async def update_my_profile(
    request: Request,
    current_user = Depends(get_current_verified_user),
    conn = Depends(get_connection)
):
    """Update current user's profile"""
    data = await request.json()
    
    # Validate profile data
    is_valid, errors = validate_profile_update(data)
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": errors}
        )
    
    # Get current profile
    profile = await conn.fetchrow("""
    SELECT id FROM profiles
    WHERE user_id = $1
    """, current_user["id"])
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    # Build update query based on provided fields
    update_fields = []
    params = [profile["id"]]  # First parameter is always profile_id
    param_idx = 2
    
    for key, value in data.items():
        if key in ["gender", "sexual_preference", "biography", "latitude", "longitude", "birth_date"]:
            update_fields.append(f"{key} = ${param_idx}")
            params.append(value)
            param_idx += 1
    
    # Add updated_at field
    update_fields.append(f"updated_at = ${param_idx}")
    params.append(datetime.utcnow())
    param_idx += 1
    
    # Check if profile would be complete after this update
    gender = data.get("gender", None)
    sexual_preference = data.get("sexual_preference", None)
    biography = data.get("biography", None)
    latitude = data.get("latitude", None)
    longitude = data.get("longitude", None)
    
    # Get existing values if not in update
    if gender is None or sexual_preference is None or biography is None or latitude is None or longitude is None:
        existing = await conn.fetchrow("""
        SELECT gender, sexual_preference, biography, latitude, longitude
        FROM profiles WHERE id = $1
        """, profile["id"])
        
        gender = gender or existing["gender"]
        sexual_preference = sexual_preference or existing["sexual_preference"]
        biography = biography or existing["biography"]
        latitude = latitude or existing["latitude"]
        longitude = longitude or existing["longitude"]
    
    # Get picture count
    pic_count = await conn.fetchval("""
    SELECT COUNT(*) FROM profile_pictures
    WHERE profile_id = $1
    """, profile["id"])
    
    # Get tag count
    tag_count = await conn.fetchval("""
    SELECT COUNT(*) FROM profile_tags
    WHERE profile_id = $1
    """, profile["id"])
    
    # Check if profile is complete
    is_complete = (
        gender is not None and 
        sexual_preference is not None and 
        biography is not None and 
        latitude is not None and 
        longitude is not None and
        pic_count > 0 and
        tag_count > 0
    )
    
    # Add is_complete to update
    update_fields.append(f"is_complete = ${param_idx}")
    params.append(is_complete)
    
    # If no fields to update, return early
    if len(update_fields) <= 2:  # Only updated_at and is_complete
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    # Execute update
    query = f"""
    UPDATE profiles
    SET {", ".join(update_fields)}
    WHERE id = $1
    RETURNING *
    """
    
    updated_profile = await conn.fetchrow(query, *params)
    
    if not updated_profile:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )
    
    # Get profile pictures
    pictures = await conn.fetch("""
    SELECT id, profile_id, file_path, backend_url, is_primary, created_at
    FROM profile_pictures
    WHERE profile_id = $1
    ORDER BY is_primary DESC, created_at ASC
    """, profile["id"])
    
    # Get profile tags
    tags = await conn.fetch("""
    SELECT t.id, t.name
    FROM tags t
    JOIN profile_tags pt ON t.id = pt.tag_id
    WHERE pt.profile_id = $1
    """, profile["id"])
    
    # Combine data
    result = dict(updated_profile)
    result["pictures"] = [dict(pic) for pic in pictures]
    result["tags"] = [dict(tag) for tag in tags]
    
    return result

@router.put("/me/tags")
async def update_my_tags(
    request: Request,
    current_user = Depends(get_current_verified_user),
    conn = Depends(get_connection)
):
    """Update current user's profile tags"""
    data = await request.json()
    tags = data.get("tags", [])
    
    # Validate tags
    is_valid, errors = validate_tags(tags)
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": errors}
        )
    
    # Get profile
    profile = await conn.fetchrow("""
    SELECT id FROM profiles
    WHERE user_id = $1
    """, current_user["id"])
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    # Update tags
    async with conn.transaction():
        # Remove all existing tags
        await conn.execute("""
        DELETE FROM profile_tags
        WHERE profile_id = $1
        """, profile["id"])
        
        # Add new tags
        for tag_name in tags:
            # Check if tag exists
            tag_id = await conn.fetchval("""
            SELECT id FROM tags
            WHERE name = $1
            """, tag_name.lower())
            
            # Create tag if it doesn't exist
            if not tag_id:
                tag_id = await conn.fetchval("""
                INSERT INTO tags (name)
                VALUES ($1)
                RETURNING id
                """, tag_name.lower())
            
            # Add tag to profile
            await conn.execute("""
            INSERT INTO profile_tags (profile_id, tag_id)
            VALUES ($1, $2)
            """, profile["id"], tag_id)
        
        # Update profile completeness
        pic_count = await conn.fetchval("""
        SELECT COUNT(*) FROM profile_pictures
        WHERE profile_id = $1
        """, profile["id"])
        
        existing = await conn.fetchrow("""
        SELECT gender, sexual_preference, biography, latitude, longitude
        FROM profiles WHERE id = $1
        """, profile["id"])
        
        is_complete = (
            len(tags) > 0 and 
            pic_count > 0 and
            existing["gender"] is not None and 
            existing["sexual_preference"] is not None and 
            existing["biography"] is not None and 
            existing["latitude"] is not None and 
            existing["longitude"] is not None
        )
        
        await conn.execute("""
        UPDATE profiles
        SET is_complete = $2, updated_at = $3
        WHERE id = $1
        """, profile["id"], is_complete, datetime.utcnow())
    
    # Get updated profile
    updated_profile = await conn.fetchrow("""
    SELECT * FROM profiles
    WHERE id = $1
    """, profile["id"])
    
    # Get profile pictures
    pictures = await conn.fetch("""
    SELECT id, profile_id, file_path, backend_url, is_primary, created_at
    FROM profile_pictures
    WHERE profile_id = $1
    ORDER BY is_primary DESC, created_at ASC
    """, profile["id"])
    
    # Get new tags
    new_tags = await conn.fetch("""
    SELECT t.id, t.name
    FROM tags t
    JOIN profile_tags pt ON t.id = pt.tag_id
    WHERE pt.profile_id = $1
    """, profile["id"])
    
    # Combine data
    result = dict(updated_profile)
    result["pictures"] = [dict(pic) for pic in pictures]
    result["tags"] = [dict(tag) for tag in new_tags]
    
    return result

@router.put("/me/location")
async def update_location(
    request: Request,
    current_user = Depends(get_current_verified_user),
    conn = Depends(get_connection)
):
    """Update current user's location"""
    data = await request.json()
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    
    if latitude is None or longitude is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Latitude and longitude are required"
        )
    
    # Validate coordinates
    if latitude < -90 or latitude > 90:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Latitude must be between -90 and 90"
        )
    
    if longitude < -180 or longitude > 180:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Longitude must be between -180 and 180"
        )
    
    # Get profile
    profile = await conn.fetchrow("""
    SELECT id, gender, sexual_preference, biography, is_complete
    FROM profiles
    WHERE user_id = $1
    """, current_user["id"])
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    # Update location
    await conn.execute("""
    UPDATE profiles
    SET latitude = $2, longitude = $3, updated_at = $4
    WHERE id = $1
    """, profile["id"], latitude, longitude, datetime.utcnow())
    
    # Check if profile would be complete after this update
    pic_count = await conn.fetchval("""
    SELECT COUNT(*) FROM profile_pictures
    WHERE profile_id = $1
    """, profile["id"])
    
    tag_count = await conn.fetchval("""
    SELECT COUNT(*) FROM profile_tags
    WHERE profile_id = $1
    """, profile["id"])
    
    is_complete = (
        profile["gender"] is not None and 
        profile["sexual_preference"] is not None and 
        profile["biography"] is not None and 
        latitude is not None and 
        longitude is not None and
        pic_count > 0 and
        tag_count > 0
    )
    
    if is_complete != profile["is_complete"]:
        await conn.execute("""
        UPDATE profiles
        SET is_complete = $2
        WHERE id = $1
        """, profile["id"], is_complete)
    
    # Get updated profile
    updated_profile = await conn.fetchrow("""
    SELECT * FROM profiles
    WHERE id = $1
    """, profile["id"])
    
    # Get profile pictures
    pictures = await conn.fetch("""
    SELECT id, profile_id, file_path, backend_url, is_primary, created_at
    FROM profile_pictures
    WHERE profile_id = $1
    ORDER BY is_primary DESC, created_at ASC
    """, profile["id"])
    
    # Get profile tags
    tags = await conn.fetch("""
    SELECT t.id, t.name
    FROM tags t
    JOIN profile_tags pt ON t.id = pt.tag_id
    WHERE pt.profile_id = $1
    """, profile["id"])
    
    # Combine data
    result = dict(updated_profile)
    result["pictures"] = [dict(pic) for pic in pictures]
    result["tags"] = [dict(tag) for tag in tags]
    
    return result

@router.post("/me/pictures")
async def upload_profile_picture(
    is_primary: bool = Form(False),
    file: UploadFile = File(...),
    current_user = Depends(get_current_verified_user),
    conn = Depends(get_connection)
):
    """Upload a profile picture"""
    # Get profile
    profile = await conn.fetchrow("""
    SELECT id FROM profiles
    WHERE user_id = $1
    """, current_user["id"])
    
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
            detail=f"Unsupported file type. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    # Check picture count limit
    pic_count = await conn.fetchval("""
    SELECT COUNT(*) FROM profile_pictures
    WHERE profile_id = $1
    """, profile["id"])
    
    if pic_count >= 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum number of pictures reached (5)"
        )
    
    # Create upload directory
    upload_dir = os.path.join(settings.MEDIA_ROOT, "profile_pictures", str(profile["id"]))
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate filename and save file
    filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(upload_dir, filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Normalize file path for database
    relative_path = os.path.relpath(file_path, start=os.path.dirname(settings.MEDIA_ROOT))
    
    # Create backend URL
    backend_url = f"{settings.BACKEND_URL}/{relative_path.replace(os.sep, '/')}"
    
    # If this is the first picture or primary is specified, make it primary
    if pic_count == 0 or is_primary:
        # Unset any existing primary pictures
        await conn.execute("""
        UPDATE profile_pictures
        SET is_primary = false
        WHERE profile_id = $1
        """, profile["id"])
        
        is_primary = True
    
    # Add picture to database
    picture = await conn.fetchrow("""
    INSERT INTO profile_pictures (profile_id, file_path, backend_url, is_primary)
    VALUES ($1, $2, $3, $4)
    RETURNING id, profile_id, file_path, backend_url, is_primary, created_at
    """, profile["id"], relative_path, backend_url, is_primary)
    
    # Check if profile is complete
    existing = await conn.fetchrow("""
    SELECT gender, sexual_preference, biography, latitude, longitude
    FROM profiles WHERE id = $1
    """, profile["id"])
    
    tag_count = await conn.fetchval("""
    SELECT COUNT(*) FROM profile_tags
    WHERE profile_id = $1
    """, profile["id"])
    
    is_complete = (
        pic_count + 1 > 0 and 
        tag_count > 0 and
        existing["gender"] is not None and 
        existing["sexual_preference"] is not None and 
        existing["biography"] is not None and 
        existing["latitude"] is not None and 
        existing["longitude"] is not None
    )
    
    await conn.execute("""
    UPDATE profiles
    SET is_complete = $2, updated_at = $3
    WHERE id = $1
    """, profile["id"], is_complete, datetime.utcnow())
    
    return dict(picture)

@router.put("/me/pictures/{picture_id}/primary")
async def set_primary_profile_picture(
    picture_id: int,
    current_user = Depends(get_current_verified_user),
    conn = Depends(get_connection)
):
    """Set a profile picture as primary"""
    # Get profile
    profile = await conn.fetchrow("""
    SELECT id FROM profiles
    WHERE user_id = $1
    """, current_user["id"])
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    # Check if picture exists
    picture = await conn.fetchrow("""
    SELECT id FROM profile_pictures
    WHERE id = $1 AND profile_id = $2
    """, picture_id, profile["id"])
    
    if not picture:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Picture not found"
        )
    
    # Update all pictures to not be primary
    await conn.execute("""
    UPDATE profile_pictures
    SET is_primary = false
    WHERE profile_id = $1
    """, profile["id"])
    
    # Set this picture as primary
    await conn.execute("""
    UPDATE profile_pictures
    SET is_primary = true
    WHERE id = $1
    """, picture_id)
    
    # Get updated picture
    updated_picture = await conn.fetchrow("""
    SELECT id, profile_id, file_path, backend_url, is_primary, created_at
    FROM profile_pictures
    WHERE id = $1
    """, picture_id)
    
    return dict(updated_picture)

@router.delete("/me/pictures/{picture_id}")
async def delete_profile_picture(
    picture_id: int,
    current_user = Depends(get_current_verified_user),
    conn = Depends(get_connection)
):
    """Delete a profile picture"""
    # Get profile
    profile = await conn.fetchrow("""
    SELECT id FROM profiles
    WHERE user_id = $1
    """, current_user["id"])
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    # Get picture
    picture = await conn.fetchrow("""
    SELECT id, file_path, is_primary FROM profile_pictures
    WHERE id = $1 AND profile_id = $2
    """, picture_id, profile["id"])
    
    if not picture:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Picture not found"
        )
    
    # Check if this is the primary picture
    was_primary = picture["is_primary"]
    
    # Delete picture from filesystem
    file_path = os.path.join(settings.MEDIA_ROOT, picture["file_path"])
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # Delete picture from database
    await conn.execute("""
    DELETE FROM profile_pictures
    WHERE id = $1
    """, picture_id)
    
    # If this was the primary picture, set a new primary
    if was_primary:
        # Get another picture to make primary
        another_picture = await conn.fetchval("""
        SELECT id FROM profile_pictures
        WHERE profile_id = $1
        LIMIT 1
        """, profile["id"])
        
        if another_picture:
            await conn.execute("""
            UPDATE profile_pictures
            SET is_primary = true
            WHERE id = $1
            """, another_picture)
    
    # Check if profile is still complete
    pic_count = await conn.fetchval("""
    SELECT COUNT(*) FROM profile_pictures
    WHERE profile_id = $1
    """, profile["id"])
    
    existing = await conn.fetchrow("""
    SELECT gender, sexual_preference, biography, latitude, longitude, is_complete
    FROM profiles WHERE id = $1
    """, profile["id"])
    
    tag_count = await conn.fetchval("""
    SELECT COUNT(*) FROM profile_tags
    WHERE profile_id = $1
    """, profile["id"])
    
    is_complete = (
        pic_count > 0 and 
        tag_count > 0 and
        existing["gender"] is not None and 
        existing["sexual_preference"] is not None and 
        existing["biography"] is not None and 
        existing["latitude"] is not None and 
        existing["longitude"] is not None
    )
    
    if is_complete != existing["is_complete"]:
        await conn.execute("""
        UPDATE profiles
        SET is_complete = $2, updated_at = $3
        WHERE id = $1
        """, profile["id"], is_complete, datetime.utcnow())
    
    return {"message": "Picture deleted successfully"}


@router.get("/suggested")
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
        example=["müzik", "kitap"]
    ),
    current_user = Depends(get_current_verified_user),
    conn = Depends(get_connection)
):
    """
    Get suggested profiles with age-based filtering
    """
    # Get user's profile
    profile = await conn.fetchrow("""
    SELECT id, is_complete FROM profiles
    WHERE user_id = $1
    """, current_user["id"])
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profil bulunamadı"
        )
    
    # Check if profile is complete
    if not profile["is_complete"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lütfen profilinizi tamamlayın"
        )
    
    try:
        # Use a modified approach for getting suggested profiles
        # Get blocks in both directions
        blocked_ids = await conn.fetch("""
        SELECT blocked_id FROM blocks WHERE blocker_id = $1
        UNION
        SELECT blocker_id FROM blocks WHERE blocked_id = $1
        """, profile["id"])
        
        # Convert to list of IDs
        excluded_ids = [row['blocked_id'] for row in blocked_ids]
        # Add user's own profile ID
        excluded_ids.append(profile["id"])
        
        # Base query parts
        select_part = """
        SELECT p.id, p.user_id, p.gender, p.sexual_preference, p.biography,
               p.latitude, p.longitude, p.fame_rating, p.birth_date,
               u.username, u.first_name, u.last_name, u.is_online, u.last_online
        FROM profiles p
        JOIN users u ON p.user_id = u.id
        """
        
        where_parts = ["p.is_complete = true"]
        
        # Handle the excluded IDs
        if excluded_ids:
            excluded_placeholders = ','.join(f"${i+1}" for i in range(len(excluded_ids)))
            where_parts.append(f"p.id NOT IN ({excluded_placeholders})")
        
        # Build parameters list starting with excluded IDs
        params = excluded_ids.copy()
        param_idx = len(params) + 1
        
        # Add filters for age, fame, distance if provided
        if min_age is not None:
            max_birth_date = datetime.utcnow() - timedelta(days=min_age*365.25)
            where_parts.append(f"p.birth_date <= ${param_idx}")
            params.append(max_birth_date)
            param_idx += 1
        
        if max_age is not None:
            min_birth_date = datetime.utcnow() - timedelta(days=(max_age+1)*365.25)
            where_parts.append(f"p.birth_date >= ${param_idx}")
            params.append(min_birth_date)
            param_idx += 1
        
        if min_fame is not None:
            where_parts.append(f"p.fame_rating >= ${param_idx}")
            params.append(min_fame)
            param_idx += 1
        
        if max_fame is not None:
            where_parts.append(f"p.fame_rating <= ${param_idx}")
            params.append(max_fame)
            param_idx += 1
        
        # Add tag filters
        if tags and len(tags) > 0:
            tag_conditions = []
            for tag in tags:
                tag_conditions.append(f"""
                EXISTS (
                    SELECT 1 FROM profile_tags pt
                    JOIN tags t ON pt.tag_id = t.id
                    WHERE pt.profile_id = p.id AND LOWER(t.name) = LOWER(${param_idx})
                )
                """)
                params.append(tag)
                param_idx += 1
            
            if tag_conditions:
                where_parts.append(f"({' AND '.join(tag_conditions)})")
        
        # Complete the query
        where_clause = " AND ".join(where_parts)
        order_clause = "ORDER BY p.fame_rating DESC, u.is_online DESC, u.last_online DESC"
        limit_clause = f"LIMIT ${param_idx} OFFSET ${param_idx+1}"
        params.extend([limit, offset])
        
        query = f"{select_part} WHERE {where_clause} {order_clause} {limit_clause}"
        
        # Execute query
        profiles_data = await conn.fetch(query, *params)
        
        # Get additional data for each profile
        results = []
        for profile_data in profiles_data:
            profile_dict = dict(profile_data)
            
            # Get profile pictures
            pictures = await conn.fetch("""
            SELECT id, profile_id, file_path, backend_url, is_primary
            FROM profile_pictures
            WHERE profile_id = $1
            ORDER BY is_primary DESC, created_at ASC
            """, profile_dict["id"])
            
            # Get profile tags
            tags = await conn.fetch("""
            SELECT t.id, t.name
            FROM tags t
            JOIN profile_tags pt ON t.id = pt.tag_id
            WHERE pt.profile_id = $1
            """, profile_dict["id"])
            
            # Add pictures and tags to the profile data
            profile_dict["pictures"] = [dict(pic) for pic in pictures]
            profile_dict["tags"] = [dict(tag) for tag in tags]
            
            results.append(profile_dict)
        
        return results
        
    except Exception as e:
        # Log the exception details for debugging
        print(f"Error in get_suggested: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching suggested profiles: {str(e)}"
        )
    
@router.get("/me/is-liked/{username}")
async def check_if_liked(
    username: str,
    current_user = Depends(get_current_verified_user),
    conn = Depends(get_connection)
):
    """
    Check if current user has liked a profile
    """
    try:
        # Get target profile by username
        target_profile = await conn.fetchrow("""
        SELECT p.id 
        FROM profiles p
        JOIN users u ON p.user_id = u.id
        WHERE u.username = $1
        """, username)
        
        if not target_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hedef profil bulunamadı"
            )
        
        # Get current user's profile
        current_profile = await conn.fetchrow("""
        SELECT id FROM profiles 
        WHERE user_id = $1
        """, current_user["id"])
        
        if not current_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profil bulunamadı"
            )
        
        # Check if the user has liked the target profile
        like = await conn.fetchval("""
        SELECT id FROM likes
        WHERE liker_id = $1 AND liked_id = $2
        """, current_profile["id"], target_profile["id"])
        
        return {"is_liked": like is not None}
        
    except Exception as e:
        import logging
        logging.error(f"Error in check_if_liked: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    
@router.get("/get-for-chat/{username}")
async def get_profile(
    username: str,
    current_user = Depends(get_current_verified_user),
    conn = Depends(get_connection)
):
    """
    Get a profile by username
    """
    try:
        # Get basic profile info
        profile_user = await conn.fetchrow("""
        SELECT p.id, p.user_id, p.gender, p.sexual_preference, p.biography,
               p.latitude, p.longitude, p.fame_rating, p.birth_date,
               u.username, u.first_name, u.last_name, u.is_online, u.last_online
        FROM profiles p
        JOIN users u ON p.user_id = u.id
        WHERE u.username = $1
        """, username)
        
        if not profile_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        # Get profile pictures
        pictures = await conn.fetch("""
        SELECT id, profile_id, file_path, backend_url, is_primary, created_at
        FROM profile_pictures
        WHERE profile_id = $1
        ORDER BY is_primary DESC, created_at ASC
        """, profile_user["id"])
        
        # Get profile tags
        tags = await conn.fetch("""
        SELECT t.id, t.name
        FROM tags t
        JOIN profile_tags pt ON t.id = pt.tag_id
        WHERE pt.profile_id = $1
        """, profile_user["id"])
        
        # Combine all data into a single response
        profile_dict = dict(profile_user)
        profile_dict["pictures"] = [dict(pic) for pic in pictures]
        profile_dict["tags"] = [dict(tag) for tag in tags]
        
        return profile_dict
        
    except Exception as e:
        import logging
        logging.error(f"Error in get_profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching profile: {str(e)}"
        )