# app/api/realtime.py
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect, Request
from typing import Dict, Any
import json
import logging

from app.core.db import get_connection
from app.core.security import get_current_verified_user
from app.db.realtime import (
    create_notification,
    get_notifications,
    mark_notification_as_read,
    mark_all_notifications_as_read,
    get_unread_notification_count,
    send_message,
    get_messages,
    get_unread_message_count
)

from jose import jwt, JWTError
from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# WebSocket connection manager for real-time features
class ConnectionManager:
    def __init__(self):
        # active_connections maps user_id to WebSocket
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        logger.info(f"WebSocket connected for user: {user_id}")
    
    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            logger.info(f"WebSocket disconnected for user: {user_id}")
    
    async def send_personal_message(self, message: Any, user_id: str):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(json.dumps(message))
            logger.debug(f"Sent message to user {user_id}: {message}")
    
    async def broadcast(self, message: Any):
        for user_id, connection in self.active_connections.items():
            await connection.send_text(json.dumps(message))
            logger.debug(f"Broadcast message to user {user_id}")

# Create connection manager instance
manager = ConnectionManager()

async def broadcast_notification(
    manager: ConnectionManager,
    user_id: str, 
    notification_type: str, 
    sender_id: str = None, 
    content: str = None
):
    """
    Broadcast a notification to a user over WebSocket if they're connected
    """
    try:
        if user_id in manager.active_connections:
            notification_data = {
                "type": "notification",
                "data": {
                    "type": notification_type,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
            if sender_id:
                notification_data["data"]["sender_id"] = sender_id
                
            if content:
                notification_data["data"]["content"] = content
                
            await manager.send_personal_message(notification_data, user_id)
            logger.info(f"Sent {notification_type} notification to user {user_id}")
    except Exception as e:
        logger.error(f"Error broadcasting notification: {str(e)}")

def verify_jwt_token(token):
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None

@router.websocket("/ws/{token}")
async def websocket_endpoint(
    websocket: WebSocket, 
    token: str,
    conn = Depends(get_connection)
):
    """
    WebSocket endpoint for real-time features
    Uses JWT token for authentication
    """
    try:
        # Get user from token
        user = None
        try:
            # Verify the token and get the payload
            payload = verify_jwt_token(token)
            user_id = payload.get("sub")
            
            if user_id:
                user = await conn.fetchrow("""
                SELECT id, username, email, first_name, last_name, 
                       is_active, is_verified
                FROM users
                WHERE id = $1
                """, user_id)
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            await websocket.close(code=1008)  # Policy violation
            return
        
        if not user:
            await websocket.close(code=1008)  # Policy violation
            return
        
        # Accept connection
        await manager.connect(websocket, user["id"])
        
        # Update online status
        await conn.execute("""
        UPDATE users
        SET is_online = true, last_login = $2
        WHERE id = $1
        """, user["id"], datetime.utcnow())
        
        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                # Handle different message types
                if message_data["type"] == "message":
                    # Send chat message
                    recipient_id = message_data["recipientId"]
                    content = message_data["content"]
                    
                    # Create message in database
                    message = await send_message(conn, user["id"], recipient_id, content)
                    
                    if message:
                        # Get sender info
                        sender = await conn.fetchrow("""
                        SELECT username, first_name, last_name
                        FROM users
                        WHERE id = $1
                        """, user["id"])
                        
                        # Get recipient info
                        recipient = await conn.fetchrow("""
                        SELECT username, first_name, last_name
                        FROM users
                        WHERE id = $1
                        """, recipient_id)
                        
                        if sender and recipient:
                            # Send message to recipient if online
                            await manager.send_personal_message({
                                "type": "message",
                                "sender_id": user["id"],
                                "recipient_id": recipient_id,
                                "content": content,
                                "timestamp": message["created_at"].isoformat()
                            }, recipient_id)
                            
                            # Also send notification event
                            await manager.send_personal_message({
                                "type": "notification",
                                "data": {
                                    "type": "message",
                                    "sender_id": user["id"],
                                    "content": f"New message from {sender['first_name']}: {content[:30]}..." if len(content) > 30 else f"New message from {sender['first_name']}: {content}"
                                }
                            }, recipient_id)
                
                elif message_data["type"] == "ping":
                    # Client ping to keep connection alive and update online status
                    await conn.execute("""
                    UPDATE users
                    SET is_online = true, last_login = $2
                    WHERE id = $1
                    """, user["id"], datetime.utcnow())
                    
                    await websocket.send_text(json.dumps({"type": "pong"}))
        
        except WebSocketDisconnect:
            # Handle disconnect
            manager.disconnect(user["id"])
            
            # Update offline status
            await conn.execute("""
            UPDATE users
            SET is_online = false, last_online = $2
            WHERE id = $1
            """, user["id"], datetime.utcnow())
            
        except Exception as e:
            # Handle other exceptions
            logger.error(f"Error in WebSocket connection: {str(e)}")
            manager.disconnect(user["id"])
            
            # Update offline status
            await conn.execute("""
            UPDATE users
            SET is_online = false, last_online = $2
            WHERE id = $1
            """, user["id"], datetime.utcnow())
    
    except Exception as e:
        # Handle connection initialization errors
        logger.error(f"WebSocket connection error: {str(e)}")




@router.get("/notifications")
async def read_notifications(
    limit: int = 20,
    offset: int = 0,
    unread_only: bool = False,
    current_user = Depends(get_current_verified_user),
    conn = Depends(get_connection)
):
    """Get notifications for current user"""
    notifications = await get_notifications(conn, current_user["id"], limit, offset, unread_only)
    
    # Format response
    formatted_notifications = []
    for notification in notifications:
        formatted_notification = dict(notification)
        formatted_notifications.append(formatted_notification)
    
    return formatted_notifications


@router.get("/notifications/count")
async def read_notification_count(
    current_user = Depends(get_current_verified_user),
    conn = Depends(get_connection)
):
    """Get unread notification count for current user"""
    count = await get_unread_notification_count(conn, current_user["id"])
    
    return {
        "count": count
    }


@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    current_user = Depends(get_current_verified_user),
    conn = Depends(get_connection)
):
    """Mark a notification as read"""
    notification_id = await mark_notification_as_read(conn, notification_id, current_user["id"])
    
    if not notification_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    return {
        "message": "Notification marked as read"
    }


@router.post("/notifications/read-all")
async def mark_all_notifications_read(
    current_user = Depends(get_current_verified_user),
    conn = Depends(get_connection)
):
    """Mark all notifications as read"""
    await mark_all_notifications_as_read(conn, current_user["id"])
    
    return {
        "message": "All notifications marked as read"
    }


@router.post("/messages")
async def create_message(
    request: Request,
    current_user = Depends(get_current_verified_user),
    conn = Depends(get_connection)
):
    """Send a message to another user"""
    data = await request.json()
    recipient_id = data.get("recipient_id")
    content = data.get("content")
    
    if not recipient_id or not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recipient ID and content are required"
        )
    
    # Send message and create notification
    message = await send_message(conn, current_user["id"], recipient_id, content)
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not send message. You might not be connected with this user."
        )
    
    # Get sender info for notification
    sender = await conn.fetchrow("""
    SELECT username, first_name, last_name
    FROM users
    WHERE id = $1
    """, current_user["id"])
    
    # Send WebSocket notification if recipient is online
    if sender:
        notification_content = f"{sender['first_name']} size yeni bir mesaj gönderdi: '{content[:30]}...'" if len(content) > 30 else f"{sender['first_name']} size yeni bir mesaj gönderdi: '{content}'"
        
        await broadcast_notification(
            manager,
            recipient_id,
            "message",
            current_user["id"],
            notification_content
        )
    
    return message


@router.get("/messages/{user_id}")
async def read_messages(
    user_id: str,
    limit: int = 50,
    offset: int = 0,
    current_user = Depends(get_current_verified_user),
    conn = Depends(get_connection)
):
    """Get messages between current user and another user"""
    messages = await get_messages(conn, current_user["id"], user_id, limit, offset)
    
    return messages


@router.get("/messages/unread/count")
async def read_unread_message_count(
    current_user = Depends(get_current_verified_user),
    conn = Depends(get_connection)
):
    """Get unread message count for current user"""
    count = await get_unread_message_count(conn, current_user["id"])
    
    return {
        "count": count
    }


@router.get("/conversations")
async def read_conversations(
    limit: int = 10,
    current_user = Depends(get_current_verified_user),
    conn = Depends(get_connection)
):
    """Get recent conversations for current user"""
    try:
        # Get active connections
        connections = await conn.fetch("""
        SELECT c.id, c.user1_id, c.user2_id, c.is_active, c.created_at, c.updated_at
        FROM connections c
        WHERE c.is_active = true AND (c.user1_id = $1 OR c.user2_id = $1)
        ORDER BY c.updated_at DESC
        LIMIT $2
        """, current_user["id"], limit)
        
        conversations = []
        for connection in connections:
            # Get the other user's ID
            other_user_id = connection["user2_id"] if connection["user1_id"] == current_user["id"] else connection["user1_id"]
            
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
            """, current_user["id"], other_user_id)
            
            # Get unread count
            unread_count = await conn.fetchval("""
            SELECT COUNT(*)
            FROM messages
            WHERE sender_id = $1 AND recipient_id = $2 AND is_read = false
            """, other_user_id, current_user["id"])
            
            # Format conversation data
            conversation = {
                "connection": dict(connection),
                "user": dict(user_info),
                "recent_message": dict(recent_message) if recent_message else None,
                "unread_count": unread_count
            }
            
            conversations.append(conversation)
        
        return conversations
    
    except Exception as e:
        logger.error(f"Error fetching conversations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching conversations: {str(e)}"
        )