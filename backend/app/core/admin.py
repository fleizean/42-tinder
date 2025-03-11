from sqlalchemy import column
from sqladmin import Admin, ModelView
from sqlalchemy.ext.asyncio import AsyncEngine
from fastapi import FastAPI
from app.core.config import settings

from app.models.user import User
from app.models.profile import Profile, Tag, ProfilePicture
from app.models.interactions import Like, Visit, Block, Report
from app.models.realtime import Notification, Message, Connection


class UserAdmin(ModelView, model=User):
    column_list = [
        User.id,
        User.username,
        User.email,
        User.first_name,
        User.last_name,
        User.is_active,
        User.is_verified,
        User.is_online,
        User.created_at
    ]
    can_create = False
    can_delete = False
    column_searchable_list = [User.username, User.email, User.first_name, User.last_name]
    column_sortable_list = [User.username, User.email, User.created_at, User.last_login]
    column_details_exclude_list = [User.hashed_password, User.verification_token, User.reset_password_token]
    
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"
    category = "User Management"


class ProfileAdmin(ModelView, model=Profile):
    column_list = [
        Profile.id,
        Profile.user_id,
        Profile.gender,
        Profile.sexual_preference,
        Profile.fame_rating,
        Profile.is_complete,
        Profile.created_at
    ]
    can_create = False
    column_searchable_list = [Profile.id, Profile.user_id]
    column_sortable_list = [Profile.fame_rating, Profile.created_at]
    
    # Define details list explicitly
    column_details_list = [
        Profile.id,
        Profile.user_id,
        Profile.gender,
        Profile.sexual_preference,
        Profile.biography,
        Profile.latitude,
        Profile.longitude, 
        Profile.fame_rating,
        Profile.is_complete,
        Profile.birth_date,
        Profile.created_at,
        Profile.updated_at
    ]
    
    name = "Profile"
    name_plural = "Profiles"
    icon = "fa-solid fa-address-card"
    category = "User Management"


class TagAdmin(ModelView, model=Tag):
    column_list = [Tag.id, Tag.name, Tag.created_at]
    column_searchable_list = [Tag.name]
    column_details_list = [Tag.id, Tag.name, Tag.created_at]
    name = "Tag"
    name_plural = "Tags"
    icon = "fa-solid fa-tag"
    category = "User Management"


class ProfilePictureAdmin(ModelView, model=ProfilePicture):
    column_list = [
        ProfilePicture.id,
        ProfilePicture.profile_id,
        ProfilePicture.file_path,
        ProfilePicture.is_primary,
        ProfilePicture.created_at
    ]
    can_create = False
    column_sortable_list = [ProfilePicture.created_at]
    column_details_list = [
        ProfilePicture.id,
        ProfilePicture.profile_id,
        ProfilePicture.file_path,
        ProfilePicture.is_primary,
        ProfilePicture.created_at
    ]

    name = "Profile Picture"
    name_plural = "Profile Pictures"
    icon = "fa-solid fa-image"
    category = "User Content"


class LikeAdmin(ModelView, model=Like):
    column_list = [Like.id, Like.liker_id, Like.liked_id, Like.created_at]
    can_create = False
    column_sortable_list = [Like.created_at]
    column_details_list = [Like.id, Like.liker_id, Like.liked_id, Like.created_at]

    name = "Like"
    name_plural = "Likes"
    icon = "fa-solid fa-heart"
    category = "Interactions"


class VisitAdmin(ModelView, model=Visit):
    column_list = [Visit.id, Visit.visitor_id, Visit.visited_id, Visit.created_at]
    can_create = False
    column_sortable_list = [Visit.created_at]
    column_details_list = [Visit.id, Visit.visitor_id, Visit.visited_id, Visit.created_at]

    name = "Visit"
    name_plural = "Visits"
    icon = "fa-solid fa-eye"
    category = "Interactions"


class BlockAdmin(ModelView, model=Block):
    column_list = [Block.id, Block.blocker_id, Block.blocked_id, Block.created_at]
    can_create = False
    column_sortable_list = [Block.created_at]
    column_details_list = [Block.id, Block.blocker_id, Block.blocked_id, Block.created_at]

    name = "Block"
    name_plural = "Blocks"
    icon = "fa-solid fa-ban"
    category = "Interactions"


class ReportAdmin(ModelView, model=Report):
    column_list = [
        Report.id,
        Report.reporter_id,
        Report.reported_id,
        Report.reason,
        #Report.description,  # Include the description field
        Report.is_resolved,
        Report.created_at,
        Report.resolved_at  # Include the resolved_at field
    ]
    can_create = False
    column_sortable_list = [Report.created_at, Report.is_resolved]
    
    # Define details list explicitly to match your model
    column_details_list = [
        Report.id,
        Report.reporter_id,
        Report.reported_id,
        Report.reason,
        #Report.description,
        Report.is_resolved,
        Report.created_at,
        Report.resolved_at
    ]
    
    name = "Report"
    name_plural = "Reports"
    icon = "fa-solid fa-flag"
    category = "Moderation"


class NotificationAdmin(ModelView, model=Notification):
    column_list = [
        Notification.id,
        Notification.user_id,
        Notification.sender_id,
        Notification.type,
        Notification.content,
        Notification.is_read,
        Notification.created_at
    ]
    can_create = False
    column_sortable_list = [Notification.created_at, Notification.is_read]
    column_details_list = [
        Notification.id,
        Notification.user_id,
        Notification.sender_id,
        Notification.type,
        Notification.content,
        Notification.is_read,
        Notification.created_at
    ]

    name = "Notification"
    name_plural = "Notifications"
    icon = "fa-solid fa-bell"
    category = "Communications"


class MessageAdmin(ModelView, model=Message):
    column_list = [
        Message.id,
        Message.sender_id,
        Message.recipient_id,
        Message.content,
        Message.is_read,
        Message.created_at
    ]
    can_create = False
    column_sortable_list = [Message.created_at]
    column_details_list = [
        Message.id,
        Message.sender_id,
        Message.recipient_id,
        Message.content,
        Message.is_read,
        Message.created_at
    ]

    name = "Message"
    name_plural = "Messages"
    icon = "fa-solid fa-message"
    category = "Communications"


class ConnectionAdmin(ModelView, model=Connection):
    column_list = [
        Connection.id,
        Connection.user1_id,
        Connection.user2_id,
        Connection.is_active,
        Connection.created_at,
        Connection.updated_at
    ]
    can_create = False
    column_sortable_list = [Connection.created_at, Connection.updated_at]
    column_details_list = [
        Connection.id,
        Connection.user1_id,
        Connection.user2_id,
        Connection.is_active,
        Connection.created_at,
        Connection.updated_at
    ]
    
    name = "Connection"
    name_plural = "Connections"
    icon = "fa-solid fa-link"
    category = "Communications"


def setup_admin(app: FastAPI, engine: AsyncEngine):
    """Set up SQLAdmin for the FastAPI app."""
    print(f"SECRET_KEY length: {len(settings.SECRET_KEY)}")
    # Ensure secret key is strong and consistent
    if len(settings.SECRET_KEY) < 32:
        print("WARNING: Secret key is too short for secure sessions")
        
    # Create an admin instance with authentication
    admin = Admin(
        app,
        engine,
        title="CrushIt Admin",
        authentication_backend=SQLAdminAuth(
            username=settings.ADMIN_USERNAME,
            password=settings.ADMIN_PASSWORD
        ),
        base_url="/admin"  # Try adding explicit base URL
    )
    
    # Register admin views
    admin.add_view(UserAdmin)
    admin.add_view(ProfileAdmin)
    admin.add_view(TagAdmin)
    admin.add_view(ProfilePictureAdmin)
    admin.add_view(LikeAdmin)
    admin.add_view(VisitAdmin)
    admin.add_view(BlockAdmin)
    admin.add_view(ReportAdmin)
    admin.add_view(NotificationAdmin)
    admin.add_view(MessageAdmin)
    admin.add_view(ConnectionAdmin)
    
    return admin


class SQLAdminAuth:
    """Authentication backend for SQLAdmin."""
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        # Required empty list for SQLAdmin compatibility
        self.middlewares = []
        
    async def login(self, request) -> bool:
        """Login handler that extracts credentials from the request."""
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
        if not username or not password:
            return False
        is_valid = username == self.username and password == self.password
        if is_valid:
            request.session["auth"] = True
            request.session["username"] = self.username
            print(f"Login successful, session set: {dict(request.session)}")
        return is_valid

    async def logout(self, request) -> bool:
        """Logout handler."""
        request.session.clear()
        return True
    
    async def authenticate(self, request):
        """Authentication method required by SQLAdmin."""
        print(f"Authentication check - Session contents: {dict(request.session)}")
        
        # Already authenticated
        if request.session.get("auth"):
            return True
            
        # Login attempt
        if request.url.path.endswith("/login") and request.method == "POST":
            return await self.login(request)
            
        return False