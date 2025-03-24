from datetime import datetime

async def like_profile(conn, liker_id, liked_id):
    """Like a profile"""
    # Check if already liked
    existing = await conn.fetchval("""
    SELECT id FROM likes 
    WHERE liker_id = $1 AND liked_id = $2
    """, liker_id, liked_id)
    
    if existing:
        return {"like_id": existing, "is_match": False}
    
    # Record the like
    like_id = await conn.fetchval("""
    INSERT INTO likes (liker_id, liked_id, created_at)
    VALUES ($1, $2, $3)
    RETURNING id
    """, liker_id, liked_id, datetime.utcnow())
    
    # Check if it's a match (mutual like)
    mutual_like = await conn.fetchval("""
    SELECT id FROM likes
    WHERE liker_id = $1 AND liked_id = $2
    """, liked_id, liker_id)
    
    is_match = mutual_like is not None
    
    # If it's a match, create or reactivate a connection
    if is_match:
        # Get user IDs for both profiles
        liker_user_id = await conn.fetchval("SELECT user_id FROM profiles WHERE id = $1", liker_id)
        liked_user_id = await conn.fetchval("SELECT user_id FROM profiles WHERE id = $1", liked_id)
        
        # Check if connection already exists
        existing_conn = await conn.fetchrow("""
        SELECT id, is_active FROM connections
        WHERE (user1_id = $1 AND user2_id = $2) OR (user1_id = $2 AND user2_id = $1)
        """, liker_user_id, liked_user_id)
        
        if existing_conn:
            # Reactivate if inactive
            if not existing_conn['is_active']:
                await conn.execute("""
                UPDATE connections
                SET is_active = true, updated_at = $3
                WHERE id = $1
                """, existing_conn['id'], datetime.utcnow())
        else:
            # Create new connection
            await conn.execute("""
            INSERT INTO connections (user1_id, user2_id, is_active, created_at, updated_at)
            VALUES ($1, $2, true, $3, $3)
            """, liker_user_id, liked_user_id, datetime.utcnow())
    
    return {"like_id": like_id, "is_match": is_match}

async def unlike_profile(conn, liker_id, liked_id):
    """Unlike a profile"""
    # Check if it was a match
    mutual_like = await conn.fetchval("""
    SELECT id FROM likes
    WHERE liker_id = $1 AND liked_id = $2
    """, liked_id, liker_id)
    
    was_match = mutual_like is not None
    
    # Remove the like
    deleted = await conn.fetchval("""
    DELETE FROM likes
    WHERE liker_id = $1 AND liked_id = $2
    RETURNING id
    """, liker_id, liked_id)
    
    if not deleted:
        return None
    
    # If it was a match, deactivate the connection
    if was_match:
        liker_user_id = await conn.fetchval("SELECT user_id FROM profiles WHERE id = $1", liker_id)
        liked_user_id = await conn.fetchval("SELECT user_id FROM profiles WHERE id = $1", liked_id)
        
        await conn.execute("""
        UPDATE connections
        SET is_active = false, updated_at = $3
        WHERE (user1_id = $1 AND user2_id = $2) OR (user1_id = $2 AND user2_id = $1)
        """, liker_user_id, liked_user_id, datetime.utcnow())
    
    return {"unliked": True, "was_match": was_match}

async def visit_profile(conn, visitor_id, visited_id):
    """Record a profile visit"""
    visit_id = await conn.fetchval("""
    INSERT INTO visits (visitor_id, visited_id, created_at)
    VALUES ($1, $2, $3)
    RETURNING id
    """, visitor_id, visited_id, datetime.utcnow())
    
    return visit_id

async def is_profile_liked(conn, liker_id, liked_id):
    """Check if a profile is liked"""
    like_id = await conn.fetchval("""
    SELECT id FROM likes
    WHERE liker_id = $1 AND liked_id = $2
    """, liker_id, liked_id)
    
    return like_id is not None

async def get_matches(conn, user_id, limit=10, offset=0):
    """Get matches for a user"""
    # Get the user's profile ID
    profile_id = await conn.fetchval("SELECT id FROM profiles WHERE user_id = $1", user_id)
    
    if not profile_id:
        return []
    
    # Get profiles that have mutual likes with the user
    query = """
    SELECT p.id, p.user_id, p.gender, p.sexual_preference, p.biography,
           p.latitude, p.longitude, p.fame_rating, p.is_complete,
           p.birth_date, u.username, u.first_name, u.last_name,
           u.is_online, u.last_online
    FROM profiles p
    JOIN users u ON p.user_id = u.id
    WHERE p.id IN (
        SELECT l1.liked_id
        FROM likes l1
        JOIN likes l2 ON l1.liker_id = l2.liked_id AND l1.liked_id = l2.liker_id
        WHERE l1.liker_id = $1
    )
    ORDER BY u.is_online DESC, u.last_online DESC
    LIMIT $2 OFFSET $3
    """
    matches = await conn.fetch(query, profile_id, limit, offset)
    
    # Get additional data for each match
    result = []
    for match in matches:
        # Get profile pictures
        pictures = await conn.fetch("""
        SELECT id, profile_id, file_path, backend_url, is_primary, created_at
        FROM profile_pictures
        WHERE profile_id = $1
        ORDER BY is_primary DESC, created_at ASC
        """, match['id'])
        
        # Get profile tags
        tags = await conn.fetch("""
        SELECT t.id, t.name
        FROM tags t
        JOIN profile_tags pt ON t.id = pt.tag_id
        WHERE pt.profile_id = $1
        """, match['id'])
        
        # Add to result
        result.append({
            "profile": dict(match),
            "pictures": [dict(pic) for pic in pictures],
            "tags": [dict(tag) for tag in tags]
        })
    
    return result