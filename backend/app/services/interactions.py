from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_
from datetime import datetime
from sqlalchemy.orm import selectinload
from app.models.interactions import Like, Visit, Block, Report
from app.models.realtime import Message, Notification, NotificationType, Connection
from app.models.profile import Profile
from app.models.user import User
from app.services.profile import update_fame_rating


async def like_profile(db: AsyncSession, liker_id: str, liked_id: str) -> Optional[Dict[str, Any]]:
    """
    Like a profile
    Returns the like object and a boolean indicating if it's a match
    """
    # Check if profiles exist
    liker_result = await db.execute(select(Profile).filter(Profile.id == liker_id))
    liker = liker_result.scalars().first()
    
    liked_result = await db.execute(select(Profile).filter(Profile.id == liked_id))
    liked = liked_result.scalars().first()
    
    if not liker or not liked:
        return None
    
    # Check if already liked
    result = await db.execute(
        select(Like).filter(Like.liker_id == liker_id, Like.liked_id == liked_id)
    )
    existing_like = result.scalars().first()
    
    if existing_like:
        return {"like": existing_like, "is_match": False}
    
    # Check if blocked
    result = await db.execute(
        select(Block).filter(
            or_(
                and_(Block.blocker_id == liker_id, Block.blocked_id == liked_id),
                and_(Block.blocker_id == liked_id, Block.blocked_id == liker_id)
            )
        )
    )
    if result.scalars().first():
        return None
    
    # Create like
    like = Like(
        liker_id=liker_id,
        liked_id=liked_id
    )
    
    db.add(like)
    await db.commit()
    await db.refresh(like)
    
    # Check if it's a match (mutual like)
    result = await db.execute(
        select(Like).filter(Like.liker_id == liked_id, Like.liked_id == liker_id)
    )
    mutual_like = result.scalars().first()
    
    is_match = mutual_like is not None
    
    # Get user info for notifications
    liker_user_result = await db.execute(select(User).filter(User.id == liker.user_id))
    liker_user = liker_user_result.scalars().first()
    
    liked_user_result = await db.execute(select(User).filter(User.id == liked.user_id))
    liked_user = liked_user_result.scalars().first()
    
    # If it's a match, create a connection
    if is_match:
        # Check if connection already exists
        result = await db.execute(
            select(Connection).filter(
                or_(
                    and_(Connection.user1_id == liker.user_id, Connection.user2_id == liked.user_id),
                    and_(Connection.user1_id == liked.user_id, Connection.user2_id == liker.user_id)
                )
            )
        )
        existing_connection = result.scalars().first()
        
        if not existing_connection:
            # Create new connection
            connection = Connection(
                user1_id=liker.user_id,
                user2_id=liked.user_id,
                is_active=True
            )
            
            db.add(connection)
            await db.commit()
            
            # Create match notifications for both users with improved content
            liker_notification = Notification(
                user_id=liker.user_id,
                sender_id=liked.user_id,
                type=NotificationType.MATCH,
                content=f"{liked_user.first_name} ile eşleştiniz! Şimdi sohbet edebilirsiniz."
            )
            
            liked_notification = Notification(
                user_id=liked.user_id,
                sender_id=liker.user_id,
                type=NotificationType.MATCH,
                content=f"{liker_user.first_name} ile eşleştiniz! Şimdi sohbet edebilirsiniz."
            )
            
            db.add(liker_notification)
            db.add(liked_notification)
            await db.commit()
        elif not existing_connection.is_active:
            # Reactivate connection if it was inactive
            existing_connection.is_active = True
            db.add(existing_connection)
            await db.commit()
            
            # Create match notifications for reconnection
            liker_notification = Notification(
                user_id=liker.user_id,
                sender_id=liked.user_id,
                type=NotificationType.MATCH,
                content=f"{liked_user.first_name} ile yeniden eşleştiniz!"
            )
            
            liked_notification = Notification(
                user_id=liked.user_id,
                sender_id=liker.user_id,
                type=NotificationType.MATCH,
                content=f"{liker_user.first_name} ile yeniden eşleştiniz!"
            )
            
            db.add(liker_notification)
            db.add(liked_notification)
            await db.commit()
    else:
        # Create like notification with more descriptive content
        notification = Notification(
            user_id=liked.user_id,
            sender_id=liker.user_id,
            type=NotificationType.LIKE,
            content=f"{liker_user.first_name} profilinizi beğendi!"
        )
        
        db.add(notification)
        await db.commit()
    
    # Update fame ratings
    await update_fame_rating(db, liked_id)
    
    return {"like": like, "is_match": is_match}

# Now let's improve the unlike_profile function to properly handle notifications

async def unlike_profile(db: AsyncSession, liker_id: str, liked_id: str) -> bool:
    """
    Unlike a profile
    """
    # Check if the like exists
    result = await db.execute(
        select(Like).filter(Like.liker_id == liker_id, Like.liked_id == liked_id)
    )
    like = result.scalars().first()
    
    if not like:
        return False
    
    # Delete like
    await db.delete(like)
    await db.commit()
    
    # Check if it was a match
    result = await db.execute(
        select(Like).filter(Like.liker_id == liked_id, Like.liked_id == liker_id)
    )
    mutual_like = result.scalars().first()
    
    if mutual_like:
        # It was a match, update connection
        # Get profiles for notification
        liker_profile_result = await db.execute(select(Profile).filter(Profile.id == liker_id))
        liker_profile = liker_profile_result.scalars().first()
        
        liked_profile_result = await db.execute(select(Profile).filter(Profile.id == liked_id))
        liked_profile = liked_profile_result.scalars().first()
        
        if liker_profile and liked_profile:
            # Get users for notification content
            liker_user_result = await db.execute(select(User).filter(User.id == liker_profile.user_id))
            liker_user = liker_user_result.scalars().first()
            
            liked_user_result = await db.execute(select(User).filter(User.id == liked_profile.user_id))
            liked_user = liked_user_result.scalars().first()
            
            # Find connection
            result = await db.execute(
                select(Connection).filter(
                    or_(
                        and_(Connection.user1_id == liker_profile.user_id, Connection.user2_id == liked_profile.user_id),
                        and_(Connection.user1_id == liked_profile.user_id, Connection.user2_id == liker_profile.user_id)
                    )
                )
            )
            connection = result.scalars().first()
            
            if connection:
                # Deactivate connection
                connection.is_active = False
                db.add(connection)
                await db.commit()
                
                # Create unmatch notification for the liked user
                notification_for_liked = Notification(
                    user_id=liked_profile.user_id,
                    sender_id=liker_profile.user_id,
                    type=NotificationType.UNMATCH,
                    content=f"{liker_user.first_name} artık eşleşmenizde değil."
                )
                
                db.add(notification_for_liked)
                
                # Create unmatch notification for the liker as well
                # This ensures both users get notified when mutual unlike happens
                notification_for_liker = Notification(
                    user_id=liker_profile.user_id,
                    sender_id=liked_profile.user_id,
                    type=NotificationType.UNMATCH,
                    content=f"{liked_user.first_name} artık eşleşmenizde değil."
                )
                
                db.add(notification_for_liker)
                await db.commit()
    
    # Update fame rating
    await update_fame_rating(db, liked_id)
    
    return True

# Let's also modify the visit_profile function to improve visit notifications

async def visit_profile(db: AsyncSession, visitor_id: str, visited_id: str) -> Optional[Visit]:
    """
    Record a profile visit
    """
    # Check if profiles exist
    visitor_result = await db.execute(select(Profile).filter(Profile.id == visitor_id))
    visitor = visitor_result.scalars().first()
    
    visited_result = await db.execute(select(Profile).filter(Profile.id == visited_id))
    visited = visited_result.scalars().first()
    
    if not visitor or not visited or visitor_id == visited_id:
        return None
    
    # Check if blocked
    result = await db.execute(
        select(Block).filter(
            or_(
                and_(Block.blocker_id == visitor_id, Block.blocked_id == visited_id),
                and_(Block.blocker_id == visited_id, Block.blocked_id == visitor_id)
            )
        )
    )
    if result.scalars().first():
        return None
    
    # Create visit
    visit = Visit(
        visitor_id=visitor_id,
        visited_id=visited_id
    )
    
    db.add(visit)
    await db.commit()
    await db.refresh(visit)
    
    # Get visitor user info for notification
    visitor_user_result = await db.execute(select(User).filter(User.id == visitor.user_id))
    visitor_user = visitor_user_result.scalars().first()
    
    # Create notification with improved content
    result = await db.execute(select(User).filter(User.id == visited.user_id))
    visited_user = result.scalars().first()
    
    if visited_user:
        notification = Notification(
            user_id=visited_user.id,
            sender_id=visitor.user_id,
            type=NotificationType.VISIT,
            content=f"{visitor_user.first_name} profilinizi ziyaret etti!"
        )
        
        db.add(notification)
        await db.commit()
    
    # Update fame rating
    await update_fame_rating(db, visited_id)
    
    return visit

# Now modify the send_message function to improve message notifications

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
    
    # Create notification with improved content
    notification = Notification(
        user_id=recipient_id,
        sender_id=sender_id,
        type=NotificationType.MESSAGE,
        content=f"{sender.first_name} size yeni bir mesaj gönderdi: '{content[:30]}...'" if len(content) > 30 else f"{sender.first_name} size yeni bir mesaj gönderdi: '{content}'"
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

async def is_blocked(db: AsyncSession, blocker_id: str, blocked_id: str) -> Dict[str, Any]:
    """
    Check if a user is blocked and return block details
    Returns:
        Dict containing:
        - is_blocked: bool
        - block_info: Dict containing block details if exists
          - block_date: datetime
          - blocker_id: str
          - blocked_id: str
    """
    result = await db.execute(
        select(Block).filter(Block.blocker_id == blocker_id, Block.blocked_id == blocked_id)
    )
    block = result.scalars().first()

    if not block:
        return {
            "is_blocked": False,
            "block_info": None
        }

    return {
        "is_blocked": True,
        "block_info": {
            "block_date": block.created_at,
            "blocker_id": block.blocker_id,
            "blocked_id": block.blocked_id
        }
    }


async def get_blocks_sent(db: AsyncSession, profile_id: str, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Get blocks sent by a profile with eagerly loaded pictures
    """
    result = await db.execute(
        select(Block, Profile, User)
        .options(selectinload(Profile.pictures))  # Eagerly load pictures
        .join(Profile, Block.blocked_id == Profile.id)
        .join(User, Profile.user_id == User.id)
        .filter(Block.blocker_id == profile_id)
        .order_by(Block.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    
    blocks_data = result.all()
    blocks = []
    
    for block, blocked_profile, blocked_user in blocks_data:
        blocks.append({
            "block": block,
            "profile": blocked_profile,
            "user": blocked_user,
        })
    
    return blocks

async def get_blocks_received(db: AsyncSession, profile_id: str, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Get blocks received by a profile
    """
    # Check if profile exists
    result = await db.execute(select(Profile).filter(Profile.id == profile_id))
    profile = result.scalars().first()
    
    if not profile:
        return []
    
    # Get blocks
    result = await db.execute(
        select(Block, Profile, User)
        .join(Profile, Block.blocker_id == Profile.id)
        .join(User, Profile.user_id == User.id)
        .filter(Block.blocked_id == profile_id)
        .order_by(Block.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    blocks_data = result.all()
    
    blocks = []
    for block, blocker_profile, blocker_user in blocks_data:
        blocks.append({
            "block": block,
            "profile": blocker_profile,
            "user": blocker_user
        })
    
    return blocks



async def block_profile(db: AsyncSession, blocker_id: str, blocked_id: str) -> Optional[Block]:
    """
    Block a profile
    """
    # Check if profiles exist
    blocker_result = await db.execute(select(Profile).filter(Profile.id == blocker_id))
    blocker = blocker_result.scalars().first()
    
    blocked_result = await db.execute(select(Profile).filter(Profile.id == blocked_id))
    blocked = blocked_result.scalars().first()
    
    if not blocker or not blocked or blocker_id == blocked_id:
        return None
    
    # Check if already blocked
    result = await db.execute(
        select(Block).filter(Block.blocker_id == blocker_id, Block.blocked_id == blocked_id)
    )
    existing_block = result.scalars().first()
    
    if existing_block:
        return existing_block
    
    # Create block
    block = Block(
        blocker_id=blocker_id,
        blocked_id=blocked_id
    )
    
    db.add(block)
    await db.commit()
    await db.refresh(block)
    
    # Remove likes in both directions
    result = await db.execute(
        select(Like).filter(
            or_(
                and_(Like.liker_id == blocker_id, Like.liked_id == blocked_id),
                and_(Like.liker_id == blocked_id, Like.liked_id == blocker_id)
            )
        )
    )
    likes = result.scalars().all()
    
    for like in likes:
        await db.delete(like)
    
    # Deactivate any connections
    result = await db.execute(
        select(Connection).filter(
            or_(
                and_(Connection.user1_id == blocker.user_id, Connection.user2_id == blocked.user_id),
                and_(Connection.user1_id == blocked.user_id, Connection.user2_id == blocker.user_id)
            )
        )
    )
    connection = result.scalars().first()
    
    if connection:
        connection.is_active = False
        db.add(connection)
    
    await db.commit()
    
    return block


async def unblock_profile(db: AsyncSession, blocker_id: str, blocked_id: str) -> bool:
    """
    Unblock a profile
    """
    # Check if the block exists
    result = await db.execute(
        select(Block).filter(Block.blocker_id == blocker_id, Block.blocked_id == blocked_id)
    )
    block = result.scalars().first()
    
    if not block:
        return False
    
    # Delete block
    await db.delete(block)
    await db.commit()
    
    return True


async def report_profile(db: AsyncSession, reporter_id: str, reported_id: str, reason: str, description: Optional[str] = None) -> Optional[Report]:
    """
    Report a profile
    """
    # Check if profiles exist
    reporter_result = await db.execute(select(Profile).filter(Profile.id == reporter_id))
    reporter = reporter_result.scalars().first()
    
    reported_result = await db.execute(select(Profile).filter(Profile.id == reported_id))
    reported = reported_result.scalars().first()
    
    if not reporter or not reported or reporter_id == reported_id:
        return None
    
    # Create report
    report = Report(
        reporter_id=reporter_id,
        reported_id=reported_id,
        reason=reason,
        description=description,
        is_resolved=False
    )
    
    db.add(report)
    await db.commit()
    await db.refresh(report)
    
    return report


async def get_likes_received(db: AsyncSession, profile_id: str, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Get likes received by a profile
    """
    # Check if profile exists
    result = await db.execute(select(Profile).filter(Profile.id == profile_id))
    profile = result.scalars().first()
    
    if not profile:
        return []
    
    # Get likes with eagerly loaded pictures and tags
    result = await db.execute(
        select(Like, Profile, User)
        .options(
            selectinload(Profile.pictures),  # Eagerly load pictures
            selectinload(Profile.tags)       # Eagerly load tags
        )
        .join(Profile, Like.liker_id == Profile.id)
        .join(User, Profile.user_id == User.id)
        .filter(Like.liked_id == profile_id)
        .order_by(Like.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    likes_data = result.all()
    
    likes = []
    for like, liker_profile, liker_user in likes_data:
        # Eagerly loaded pictures ve tags'i kullan
        likes.append({
            "like": like,
            "profile": liker_profile,
            "user": liker_user,
            # İlave olarak pictures ve tags'i açıkça ekleyelim
            "pictures": list(liker_profile.pictures) if liker_profile.pictures else [],
            "tags": list(liker_profile.tags) if liker_profile.tags else []
        })
    
    return likes


async def get_visits_received(db: AsyncSession, profile_id: str, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Get visits received by a profile
    """
    # Check if profile exists
    result = await db.execute(select(Profile).filter(Profile.id == profile_id))
    profile = result.scalars().first()
    
    if not profile:
        return []
    
    # Get visits with eagerly loaded pictures and tags
    result = await db.execute(
        select(Visit, Profile, User)
        .options(
            selectinload(Profile.pictures),  # Eagerly load pictures
            selectinload(Profile.tags)       # Eagerly load tags
        )
        .join(Profile, Visit.visitor_id == Profile.id)
        .join(User, Profile.user_id == User.id)
        .filter(Visit.visited_id == profile_id)
        .order_by(Visit.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    visits_data = result.all()
    
    visits = []
    for visit, visitor_profile, visitor_user in visits_data:
        # Eagerly loaded pictures ve tags'i kullan
        visits.append({
            "visit": visit,
            "profile": visitor_profile,
            "user": visitor_user,
            # İlave olarak pictures ve tags'i açıkça ekleyelim
            "pictures": list(visitor_profile.pictures) if visitor_profile.pictures else [],
            "tags": list(visitor_profile.tags) if visitor_profile.tags else []
        })
    
    return visits



async def get_matches(db: AsyncSession, user_id: str, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Get matches for a user
    """
    # Get user's profile
    result = await db.execute(select(Profile).filter(Profile.user_id == user_id))
    profile = result.scalars().first()
    
    if not profile:
        return []
    
    # Get active connections
    result = await db.execute(
        select(Connection, User)
        .join(User, 
            or_(
                and_(Connection.user1_id == user_id, Connection.user2_id == User.id),
                and_(Connection.user2_id == user_id, Connection.user1_id == User.id)
            )
        )
        .filter(Connection.is_active == True)
        .order_by(Connection.updated_at.desc())
        .offset(offset)
        .limit(limit)
    )
    connection_data = result.all()
    
    matches = []
    for connection, matched_user in connection_data:
        # Get the matched user's profile with pictures and tags eagerly loaded
        result = await db.execute(
            select(Profile)
            .options(selectinload(Profile.pictures), selectinload(Profile.tags))
            .filter(Profile.user_id == matched_user.id)
        )
        matched_profile = result.scalars().first()
        
        if matched_profile:
            matches.append({
                "connection": connection,
                "profile": matched_profile,
                "user": matched_user
            })
    
    return matches