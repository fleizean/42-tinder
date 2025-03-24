# app/db/realtime.py
from datetime import datetime

async def create_notification(conn, user_id, sender_id, notification_type, content=None):
    """Create a notification"""
    query = """
    INSERT INTO notifications (user_id, sender_id, type, content, is_read, created_at)
    VALUES ($1, $2, $3, $4, false, $5)
    RETURNING id, user_id, sender_id, type, content, is_read, created_at, read_at
    """
    return await conn.fetchrow(
        query, user_id, sender_id, notification_type, content, datetime.utcnow()
    )

async def get_notifications(conn, user_id, limit=20, offset=0, unread_only=False):
    """Get notifications for a user with sender information"""
    params = [user_id, limit, offset]
    
    query = """
    SELECT n.id, n.user_id, n.sender_id, n.type, n.content, 
           n.is_read, n.created_at, n.read_at,
           u.username as sender_username, u.first_name as sender_first_name,
           u.last_name as sender_last_name
    FROM notifications n
    LEFT JOIN users u ON n.sender_id = u.id
    WHERE n.user_id = $1
    """
    
    if unread_only:
        query += " AND n.is_read = false"
    
    query += """
    ORDER BY n.created_at DESC
    LIMIT $2 OFFSET $3
    """
    
    return await conn.fetch(query, *params)

async def mark_notification_as_read(conn, notification_id, user_id):
    """Mark a notification as read"""
    query = """
    UPDATE notifications
    SET is_read = true, read_at = $3
    WHERE id = $1 AND user_id = $2
    RETURNING id
    """
    return await conn.fetchval(query, notification_id, user_id, datetime.utcnow())

async def mark_all_notifications_as_read(conn, user_id):
    """Mark all notifications as read for a user"""
    query = """
    UPDATE notifications
    SET is_read = true, read_at = $2
    WHERE user_id = $1 AND is_read = false
    """
    return await conn.execute(query, user_id, datetime.utcnow())

async def get_unread_notification_count(conn, user_id):
    """Get count of unread notifications for a user"""
    query = """
    SELECT COUNT(*)
    FROM notifications
    WHERE user_id = $1 AND is_read = false
    """
    return await conn.fetchval(query, user_id)

async def send_message(conn, sender_id, recipient_id, content):
    """Send a message from one user to another"""
    # Check if users exist
    sender = await conn.fetchrow("SELECT id FROM users WHERE id = $1", sender_id)
    recipient = await conn.fetchrow("SELECT id FROM users WHERE id = $1", recipient_id)
    
    if not sender or not recipient:
        return None
    
    # Check if they are connected
    connection = await conn.fetchrow("""
    SELECT id FROM connections
    WHERE is_active = true AND 
    ((user1_id = $1 AND user2_id = $2) OR (user1_id = $2 AND user2_id = $1))
    """, sender_id, recipient_id)
    
    if not connection:
        return None
    
    # Create message
    now = datetime.utcnow()
    message = await conn.fetchrow("""
    INSERT INTO messages (sender_id, recipient_id, content, is_read, created_at)
    VALUES ($1, $2, $3, false, $4)
    RETURNING id, sender_id, recipient_id, content, is_read, created_at, read_at
    """, sender_id, recipient_id, content, now)
    
    # Create notification
    await create_notification(
        conn, recipient_id, sender_id, 'message', 
        f"New message from {sender_id}"
    )
    
    # Update connection timestamp
    await conn.execute("""
    UPDATE connections
    SET updated_at = $2
    WHERE id = $1
    """, connection['id'], now)
    
    return message

async def get_messages(conn, user1_id, user2_id, limit=50, offset=0):
    """Get messages between two users"""
    # Get messages
    query = """
    SELECT id, sender_id, recipient_id, content, is_read, created_at, read_at
    FROM messages
    WHERE (sender_id = $1 AND recipient_id = $2) OR (sender_id = $2 AND recipient_id = $1)
    ORDER BY created_at DESC
    LIMIT $3 OFFSET $4
    """
    messages = await conn.fetch(query, user1_id, user2_id, limit, offset)
    
    # Mark messages as read if recipient is user1
    now = datetime.utcnow()
    for message in messages:
        if message['recipient_id'] == user1_id and not message['is_read']:
            await conn.execute("""
            UPDATE messages
            SET is_read = true, read_at = $2
            WHERE id = $1
            """, message['id'], now)
    
    # Return messages in chronological order (oldest first)
    return [dict(msg) for msg in reversed(messages)]

async def get_unread_message_count(conn, user_id):
    """Get count of unread messages for a user"""
    query = """
    SELECT COUNT(*)
    FROM messages
    WHERE recipient_id = $1 AND is_read = false
    """
    return await conn.fetchval(query, user_id)

async def get_recent_conversations(conn, user_id, limit=10):
    """Get recent conversations for a user"""
    # Get active connections
    connections = await conn.fetch("""
    SELECT id, user1_id, user2_id, is_active, created_at, updated_at
    FROM connections
    WHERE is_active = true AND (user1_id = $1 OR user2_id = $1)
    ORDER BY updated_at DESC
    LIMIT $2
    """, user_id, limit)
    
    conversations = []
    for connection in connections:
        # Get the other user's ID
        other_user_id = connection["user2_id"] if connection["user1_id"] == user_id else connection["user1_id"]
        
        # Get user info
        user_info = await conn.fetchrow("""
        SELECT id, username, first_name, last_name, is_online, last_online
        FROM users
        WHERE id = $1
        """, other_user_id)
        
        if not user_info:
            continue
        
        # Get most recent message
        recent_message = await conn.fetchrow("""
        SELECT id, sender_id, recipient_id, content, is_read, created_at, read_at
        FROM messages
        WHERE (sender_id = $1 AND recipient_id = $2) OR (sender_id = $2 AND recipient_id = $1)
        ORDER BY created_at DESC
        LIMIT 1
        """, user_id, other_user_id)
        
        # Get unread count
        unread_count = await conn.fetchval("""
        SELECT COUNT(*)
        FROM messages
        WHERE sender_id = $1 AND recipient_id = $2 AND is_read = false
        """, other_user_id, user_id)
        
        # Format conversation data
        conversation = {
            "connection": dict(connection),
            "user": dict(user_info),
            "recent_message": dict(recent_message) if recent_message else None,
            "unread_count": unread_count
        }
        
        conversations.append(conversation)
    
    return conversations