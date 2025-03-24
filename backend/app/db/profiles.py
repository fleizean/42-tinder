import uuid
from datetime import datetime

async def get_profile_by_id(conn, profile_id):
    """Get a profile by ID"""
    query = """
    SELECT id, user_id, gender, sexual_preference, biography,
           latitude, longitude, fame_rating, is_complete,
           birth_date, created_at, updated_at
    FROM profiles
    WHERE id = $1
    """
    return await conn.fetchrow(query, profile_id)

async def get_profile_by_user_id(conn, user_id):
    """Get a profile by user ID"""
    query = """
    SELECT id, user_id, gender, sexual_preference, biography,
           latitude, longitude, fame_rating, is_complete,
           birth_date, created_at, updated_at
    FROM profiles
    WHERE user_id = $1
    """
    return await conn.fetchrow(query, user_id)

async def create_profile(conn, user_id):
    """Create a new profile for a user"""
    profile_id = str(uuid.uuid4())
    query = """
    INSERT INTO profiles (id, user_id, is_complete, fame_rating)
    VALUES ($1, $2, $3, $4)
    RETURNING id
    """
    return await conn.fetchval(query, profile_id, user_id, False, 0.0)

async def update_profile(conn, profile_id, profile_data):
    """Update profile information"""
    # Build dynamic update query based on provided fields
    fields = []
    values = [profile_id]  # First parameter is always the profile_id
    param_idx = 2

    for key, value in profile_data.items():
        if key in ['gender', 'sexual_preference', 'biography', 'latitude', 'longitude', 'birth_date', 'is_complete']:
            fields.append(f"{key} = ${param_idx}")
            values.append(value)
            param_idx += 1

    # Add updated_at field
    fields.append(f"updated_at = ${param_idx}")
    values.append(datetime.utcnow())

    # If no fields to update, return early
    if not fields:
        return None

    query = f"""
    UPDATE profiles
    SET {', '.join(fields)}
    WHERE id = $1
    RETURNING id, user_id, gender, sexual_preference, biography,
              latitude, longitude, fame_rating, is_complete, birth_date
    """
    
    return await conn.fetchrow(query, *values)

async def get_profile_pictures(conn, profile_id):
    """Get all pictures for a profile"""
    query = """
    SELECT id, profile_id, file_path, backend_url, is_primary, created_at
    FROM profile_pictures
    WHERE profile_id = $1
    ORDER BY is_primary DESC, created_at ASC
    """
    return await conn.fetch(query, profile_id)

async def add_profile_picture(conn, profile_id, file_path, backend_url, is_primary=False):
    """Add a picture to a profile"""
    # If this is primary, unset any existing primary pictures
    if is_primary:
        await conn.execute("""
        UPDATE profile_pictures
        SET is_primary = false
        WHERE profile_id = $1
        """, profile_id)
    
    query = """
    INSERT INTO profile_pictures (profile_id, file_path, backend_url, is_primary)
    VALUES ($1, $2, $3, $4)
    RETURNING id, profile_id, file_path, backend_url, is_primary, created_at
    """
    return await conn.fetchrow(query, profile_id, file_path, backend_url, is_primary)

async def set_primary_picture(conn, profile_id, picture_id):
    """Set a picture as primary for a profile"""
    # First unset all primary pictures
    await conn.execute("""
    UPDATE profile_pictures
    SET is_primary = false
    WHERE profile_id = $1
    """, profile_id)
    
    # Then set the selected picture as primary
    query = """
    UPDATE profile_pictures
    SET is_primary = true
    WHERE id = $1 AND profile_id = $2
    RETURNING id
    """
    return await conn.fetchval(query, picture_id, profile_id)

async def remove_profile_picture(conn, picture_id, profile_id):
    """Remove a picture from a profile"""
    query = """
    DELETE FROM profile_pictures
    WHERE id = $1 AND profile_id = $2
    RETURNING id, is_primary
    """
    return await conn.fetchrow(query, picture_id, profile_id)

async def get_profile_tags(conn, profile_id):
    """Get all tags for a profile"""
    query = """
    SELECT t.id, t.name
    FROM tags t
    JOIN profile_tags pt ON t.id = pt.tag_id
    WHERE pt.profile_id = $1
    """
    return await conn.fetch(query, profile_id)

async def update_profile_tags(conn, profile_id, tag_names):
    """Update a profile's tags"""
    # Start a transaction
    async with conn.transaction():
        # Remove all existing tags for the profile
        await conn.execute("""
        DELETE FROM profile_tags
        WHERE profile_id = $1
        """, profile_id)
        
        # Add each tag
        for tag_name in tag_names:
            # Check if tag exists
            tag_id = await conn.fetchval("""
            SELECT id FROM tags WHERE name = $1
            """, tag_name.lower())
            
            # Create tag if it doesn't exist
            if not tag_id:
                tag_id = await conn.fetchval("""
                INSERT INTO tags (name) VALUES ($1) RETURNING id
                """, tag_name.lower())
            
            # Add tag to profile
            await conn.execute("""
            INSERT INTO profile_tags (profile_id, tag_id)
            VALUES ($1, $2)
            ON CONFLICT DO NOTHING
            """, profile_id, tag_id)
            
    # Return the updated tags
    return await get_profile_tags(conn, profile_id)