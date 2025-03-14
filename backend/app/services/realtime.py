from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, and_, or_
from datetime import datetime

from app.models.realtime import Notification, NotificationType, Message, Connection
from app.models.user import User



async def get_notifications(db: AsyncSession, user_id: str, limit: int = 20, offset: int = 0, unread_only: bool = False) -> List[Dict[str, Any]]:
    """
    Get notifications for a user with sender username
    """
    # Base query - add username to the query
    query = select(Notification, User).outerjoin(
        User, Notification.sender_id == User.id
    ).filter(
        Notification.user_id == user_id
    ).order_by(Notification.created_at.desc())
    
    # Filter by read status if needed
    if unread_only:
        query = query.filter(Notification.is_read == False)
    
    # Execute with pagination
    result = await db.execute(query.offset(offset).limit(limit))
    notification_data = result.all()
    
    notifications = []
    for notification, sender in notification_data:
        notifications.append({
            "notification": notification,
            "sender": sender
        })
    
    return notifications


async def mark_notification_as_read(db: AsyncSession, notification_id: int, user_id: str) -> Optional[Notification]:
    """
    Mark a notification as read
    """
    # Get notification
    result = await db.execute(
        select(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        )
    )
    notification = result.scalars().first()
    
    if not notification:
        return None
    
    # Mark as read
    notification.is_read = True
    notification.read_at = datetime.utcnow()
    db.add(notification)
    await db.commit()
    await db.refresh(notification)
    
    return notification


async def mark_all_notifications_as_read(db: AsyncSession, user_id: str) -> int:
    """
    Mark all notifications as read for a user
    Returns the number of notifications updated
    """
    # Get unread notifications
    result = await db.execute(
        select(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        )
    )
    notifications = result.scalars().all()
    
    # Mark all as read
    now = datetime.utcnow()
    for notification in notifications:
        notification.is_read = True
        notification.read_at = now
        db.add(notification)
    
    await db.commit()
    
    return len(notifications)


async def get_unread_notification_count(db: AsyncSession, user_id: str) -> int:
    """
    Get the count of unread notifications for a user
    """
    result = await db.execute(
        select(func.count()).select_from(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        )
    )
    return result.scalar()


async def send_message(db: AsyncSession, sender_id: str, recipient_id: str, content: str) -> Optional[Dict[str, Any]]:
    """
    Send a message from one user to another
    """
    # Check if users exist
    sender_result = await db.execute(select(User).filter(User.id == sender_id))
    sender = sender_result.scalars().first()
    
    recipient_result = await db.execute(select(User).filter(User.id == recipient_id))
    recipient = recipient_result.scalars().first()
    
    if not sender or not recipient:
        return None
    
    # Check if they are connected
    result = await db.execute(
        select(Connection).filter(
            Connection.is_active == True,
            or_(
                and_(Connection.user1_id == sender_id, Connection.user2_id == recipient_id),
                and_(Connection.user1_id == recipient_id, Connection.user2_id == sender_id)
            )
        )
    )
    connection = result.scalars().first()
    
    if not connection:
        return None
    
    # Create message
    message = Message(
        sender_id=sender_id,
        recipient_id=recipient_id,
        content=content,
        is_read=False
    )
    
    db.add(message)
    await db.commit()
    await db.refresh(message)
    
    # Create notification
    notification = Notification(
        user_id=recipient_id,
        sender_id=sender_id,
        type=NotificationType.MESSAGE,
        content=f"You have a new message"
    )
    
    db.add(notification)
    await db.commit()
    
    # Update connection timestamp
    connection.updated_at = datetime.utcnow()
    db.add(connection)
    await db.commit()
    
    return {
        "message": message,
        "sender": sender,
        "recipient": recipient
    }


async def get_messages(db: AsyncSession, user1_id: str, user2_id: str, limit: int = 50, offset: int = 0) -> List[Message]:
    """
    Get messages between two users
    """
    # Get messages
    result = await db.execute(
        select(Message).filter(
            or_(
                and_(Message.sender_id == user1_id, Message.recipient_id == user2_id),
                and_(Message.sender_id == user2_id, Message.recipient_id == user1_id)
            )
        ).order_by(Message.created_at.desc()).offset(offset).limit(limit)
    )
    messages = result.scalars().all()
    
    # Mark messages as read if recipient is the current user
    for message in messages:
        if message.recipient_id == user1_id and not message.is_read:
            message.is_read = True
            message.read_at = datetime.utcnow()
            db.add(message)
    
    await db.commit()
    
    # Return in chronological order
    return list(reversed(messages))


async def get_unread_message_count(db: AsyncSession, user_id: str) -> int:
    """
    Get the count of unread messages for a user
    """
    result = await db.execute(
        select(func.count()).select_from(Message).filter(
            Message.recipient_id == user_id,
            Message.is_read == False
        )
    )
    return result.scalar()


async def get_recent_conversations(db: AsyncSession, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get recent conversations for a user
    """
    try:
        # Get active connections
        connections_result = await db.execute(
            select(Connection).filter(
                Connection.is_active == True,
                or_(
                    Connection.user1_id == user_id,
                    Connection.user2_id == user_id
                )
            ).order_by(Connection.updated_at.desc()).limit(limit)
        )
        connections = connections_result.scalars().all()
        
        conversations = []
        for connection in connections:
            # Get the other user
            other_user_id = connection.user2_id if connection.user1_id == user_id else connection.user1_id
            
            # Get user info
            result = await db.execute(select(User).filter(User.id == other_user_id))
            other_user = result.scalars().first()
            
            if not other_user:
                continue
            
            # Get most recent message
            result = await db.execute(
                select(Message).filter(
                    or_(
                        and_(Message.sender_id == user_id, Message.recipient_id == other_user_id),
                        and_(Message.sender_id == other_user_id, Message.recipient_id == user_id)
                    )
                ).order_by(Message.created_at.desc()).limit(1)
            )
            recent_message = result.scalars().first()
            
            # Get unread count
            result = await db.execute(
                select(func.count()).select_from(Message).filter(
                    Message.sender_id == other_user_id,
                    Message.recipient_id == user_id,
                    Message.is_read == False
                )
            )
            unread_count = result.scalar()
            
            conversations.append({
                "connection": connection,
                "user": other_user,
                "recent_message": recent_message,
                "unread_count": unread_count
            })
        
        return conversations
    except Exception as e:
        # Log the exception
        import logging
        logging.error(f"Error in get_recent_conversations: {str(e)}")
        
        # Return empty list instead of failing
        return []