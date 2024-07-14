from datetime import datetime

class User:
    def __init__(self, email, username, last_name, first_name, password, gender, birthday, sexual_preferences='', biography='', fame_rating=0, location='', verification_token='', verify_email=0, interests=None, profile_pictures=None, created_at=None, updated_at=None):
        self.email = email
        self.username = username
        self.last_name = last_name
        self.first_name = first_name
        self.password = password
        self.gender = gender
        self.sexual_preferences = sexual_preferences
        self.biography = biography
        self.fame_rating = fame_rating
        self.location = location
        self.interests = interests or []
        self.birthday = birthday
        self.verification_token = verification_token
        self.verify_email = verify_email
        self.profile_pictures = profile_pictures or []
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

class Interest:
    def __init__(self, id, name, user_id):
        self.id = id
        self.name = name
        self.user_id = user_id

class ProfilePicture:
    def __init__(self, id, image_path, is_profile_picture, user_id):
        self.id = id
        self.image_path = image_path
        self.is_profile_picture = is_profile_picture
        self.user_id = user_id

class Message:
    def __init__(self, id, sender_id, receiver_id, content, timestamp=None):
        self.id = id
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.content = content
        self.timestamp = timestamp or datetime.utcnow()

class Notification:
    def __init__(self, id, user_id, message, is_read=False, timestamp=None):
        self.id = id
        self.user_id = user_id
        self.message = message
        self.is_read = is_read
        self.timestamp = timestamp or datetime.utcnow()
