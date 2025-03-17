from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, List, Dict, Optional
import json

from app.core.db import get_db
from app.core.security import get_current_user, get_current_verified_user
from app.models.user import User
from app.schemas.realtime import Conversation, Message, MessageCreate, Notification, WebSocketMessage
from app.services.realtime import (
    get_notifications,
    mark_notification_as_read,
    mark_all_notifications_as_read,
    get_unread_notification_count,
    send_message,
    get_messages,
    get_unread_message_count,
    get_recent_conversations
)
from app.services.auth import update_last_activity
# Configure logging
import logging
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
    
    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
    
    async def send_personal_message(self, message: Any, user_id: str):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(json.dumps(message))
    
    async def broadcast(self, message: Any):
        for connection in self.active_connections.values():
            await connection.send_text(json.dumps(message))


# Create connection manager instance
manager = ConnectionManager()


@router.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str, db: AsyncSession = Depends(get_db)):
    """
    WebSocket endpoint for real-time features
    Uses JWT token for authentication
    """
    try:
        # Authenticate user with token
        user = await get_current_user(token=token, db=db)
        
        # Accept connection
        await manager.connect(websocket, user.id)
        logger.info(f"WebSocket connected for user: {user.id}")
        
        # Update online status
        await update_last_activity(db, user.id, is_online=True)
        
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
                    result = await send_message(db, user.id, recipient_id, content)
                    
                    if result:
                        # Send message to recipient if online
                        await manager.send_personal_message({
                            "type": "message",
                            "sender_id": user.id,
                            "recipient_id": recipient_id,
                            "content": content,
                            "timestamp": result["message"].created_at.isoformat()
                        }, recipient_id)
                        
                        # Also send notification event
                        await manager.send_personal_message({
                            "type": "notification",
                            "data": {
                                "type": "message",
                                "sender_id": user.id,
                                "content": f"New message from {result['sender'].first_name}: {content[:30]}..." if len(content) > 30 else f"New message from {result['sender'].first_name}: {content}"
                            }
                        }, recipient_id)
                
                elif message_data["type"] == "ping":
                    # Client ping to keep connection alive and update online status
                    await update_last_activity(db, user.id, is_online=True)
                    await websocket.send_text(json.dumps({"type": "pong"}))
        
        except WebSocketDisconnect:
            # Handle disconnect
            logger.info(f"WebSocket disconnected for user: {user.id}")
            manager.disconnect(user.id)
            await update_last_activity(db, user.id, is_online=False)
        
        except Exception as e:
            # Handle other exceptions during connection
            logger.error(f"Error in WebSocket connection for user {user.id}: {str(e)}")
            manager.disconnect(user.id)
            await update_last_activity(db, user.id, is_online=False)
    
    except Exception as e:
        # Log the exception for debugging
        logger.error(f"WebSocket authentication error: {str(e)}")
        # Handle authentication failure
        try:
            await websocket.close(code=1008)  # Policy violation
        except Exception:
            pass  # Already closed or other error

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


async def send_message_with_notification(db: AsyncSession, sender_id: str, recipient_id: str, content: str) -> Optional[Dict[str, Any]]:
    """
    Send a message from one user to another and broadcast notification
    """
    # First, use the existing send_message function
    result = await send_message(db, sender_id, recipient_id, content)
    
    if result:
        # Get sender info for notification
        sender = result["sender"]
        
        # Broadcast notification to recipient
        await broadcast_notification(
            manager,
            recipient_id,
            "message",
            sender_id,
            f"{sender.first_name} size yeni bir mesaj gönderdi: '{content[:30]}...'" if len(content) > 30 else f"{sender.first_name} size yeni bir mesaj gönderdi: '{content}'"
        )
    
    return result
        

@router.get("/notifications", response_model=List[Dict[str, Any]])
async def read_notifications(
    limit: int = 20,
    offset: int = 0,
    unread_only: bool = False,
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get notifications for current user
    """
    notifications_data = await get_notifications(db, current_user.id, limit, offset, unread_only)
    
    # Create response with both notification and sender info
    formatted_notifications = []
    for item in notifications_data:
        notification = item["notification"]
        sender = item["sender"]
        
        formatted_notification = {
            "id": notification.id,
            "user_id": notification.user_id,
            "sender_id": notification.sender_id,
            "sender_username": sender.username if sender else None,
            "type": notification.type,
            "content": notification.content,
            "is_read": notification.is_read,
            "created_at": notification.created_at,
            "read_at": notification.read_at
        }
        
        formatted_notifications.append(formatted_notification)
    
    return formatted_notifications


@router.get("/notifications/count", response_model=Dict[str, int])
async def read_notification_count(
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get unread notification count for current user
    """
    count = await get_unread_notification_count(db, current_user.id)
    
    return {
        "count": count
    }


@router.post("/notifications/{notification_id}/read", response_model=Notification)
async def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Mark a notification as read
    """
    notification = await mark_notification_as_read(db, notification_id, current_user.id)
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    return notification


@router.post("/notifications/read-all", response_model=Dict[str, int])
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Mark all notifications as read
    """
    count = await mark_all_notifications_as_read(db, current_user.id)
    
    return {
        "count": count
    }


@router.post("/messages", response_model=Message)
async def create_message(
    message_data: MessageCreate,
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Send a message to another user
    """
    result = await send_message_with_notification(db, current_user.id, message_data.recipient_id, message_data.content)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not send message. You might not be connected with this user."
        )
    
    return result["message"]


@router.get("/messages/{user_id}", response_model=List[Message])
async def read_messages(
    user_id: str,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get messages between current user and another user
    """
    messages = await get_messages(db, current_user.id, user_id, limit, offset)
    
    return messages


@router.get("/conversations", response_model=List[Conversation])
async def read_conversations(
    limit: int = 10,
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get recent conversations for current user
    """
    try:
        logger.info(f"Fetching conversations for user: {current_user.id}")
        conversations = await get_recent_conversations(db, current_user.id, limit)
        logger.info(f"Found {len(conversations)} conversations")
        
        # Convert SQLAlchemy models to Pydantic models
        pydantic_conversations = []
        for conv in conversations:
            # Create a Pydantic Conversation model
            pydantic_conversation = Conversation(
                connection=conv["connection"],
                user=conv["user"],
                recent_message=conv["recent_message"],
                unread_count=conv["unread_count"]
            )
            pydantic_conversations.append(pydantic_conversation)
        
        return pydantic_conversations
    except Exception as e:
        logger.error(f"Error fetching conversations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching conversations: {str(e)}"
        )

@router.get("/messages/unread/count", response_model=Dict[str, int])
async def read_unread_message_count(
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get unread message count for current user
    """
    count = await get_unread_message_count(db, current_user.id)
    
    return {
        "count": count
    }