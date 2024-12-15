import sqlite3
from datetime import datetime

class User:
    def __init__(self, id, email, username, last_name, first_name, password, gender, sexual_preferences, biography, fame_rating, comment_count, match_count, latitude, longitude, birthday, verification_token, verify_email, created_at=None, updated_at=None, profile_pictures=None, interests=None):
        self.id = id
        self.email = email
        self.username = username
        self.last_name = last_name
        self.first_name = first_name
        self.password = password
        self.gender = gender
        self.sexual_preferences = sexual_preferences
        self.biography = biography
        self.fame_rating = fame_rating
        self.comment_count = comment_count
        self.match_count = match_count
        self.latitude = latitude
        self.longitude = longitude
        self.birthday = birthday
        self.verification_token = verification_token
        self.verify_email = verify_email
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.profile_pictures = profile_pictures or []
        self.interests = interests or []

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'last_name': self.last_name,
            'first_name': self.first_name,
            'gender': self.gender,
            'sexual_preferences': self.sexual_preferences,
            'biography': self.biography,
            'fame_rating': self.fame_rating,
            'comment_count': self.comment_count,
            'match_count': self.match_count,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'birthday': self.birthday,
            'interests': [interest.to_dict() for interest in self.interests],
            'profile_pictures': [picture.to_dict() for picture in self.profile_pictures],
        }

    @classmethod
    def get_by_id(cls, user_id):
        with sqlite3.connect('database.db') as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user_data = c.fetchone()
            if user_data:
                user = cls(*user_data)
                user.profile_pictures = ProfilePicture.get_by_user_id(user_id)
                user.interests = Interest.get_by_user_id(user_id)
                return user
            return None

    @classmethod
    def get_by_email(cls, email):
        with sqlite3.connect('database.db') as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE email = ?", (email,))
            user_data = c.fetchone()
            if user_data:
                user = cls(*user_data)
                user.profile_pictures = ProfilePicture.get_by_user_id(user_data[0])
                user.interests = Interest.get_by_user_id(user_data[0])
                return user
            return None

    @classmethod
    def get_by_username(cls, username):
        with sqlite3.connect('database.db') as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE username = ?", (username,))
            user_data = c.fetchone()
            if user_data:
                user = cls(*user_data)
                user.profile_pictures = ProfilePicture.get_by_user_id(user_data[0])
                user.interests = Interest.get_by_user_id(user_data[0])
                return user
            return None

    @classmethod
    def get_by_verification_token(cls, token):
        with sqlite3.connect('database.db') as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE verification_token = ?", (token,))
            user_data = c.fetchone()
            if user_data:
                user = cls(*user_data)
                user.profile_pictures = ProfilePicture.get_by_user_id(user_data[0])
                user.interests = Interest.get_by_user_id(user_data[0])
                return user
            return None

    @classmethod
    def get_all(cls):
        with sqlite3.connect('database.db') as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM users")
            users_data = c.fetchall()
            users = []
            for user_data in users_data:
                user = cls(*user_data)
                user.profile_pictures = ProfilePicture.get_by_user_id(user.id)
                user.interests = Interest.get_by_user_id(user.id)
                users.append(user)
            return users


class Interest:
    def __init__(self, id=None, name=None, user_id=None):
        self.id = id
        self.name = name
        self.user_id = user_id
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'user_id': self.user_id
        }
    
    def save(self):
        with sqlite3.connect('database.db') as conn:
            c = conn.cursor()
            c.execute("INSERT INTO interests (name, user_id) VALUES (?, ?)", (self.name, self.user_id))
            conn.commit()
    
    def delete(self):
        with sqlite3.connect('database.db') as conn:
            c = conn.cursor()
            c.execute("DELETE FROM interests WHERE id = ?", (self.id,))
            conn.commit()

    @classmethod
    def get_by_user_id(cls, user_id):
        with sqlite3.connect('database.db') as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM interests WHERE user_id = ?", (user_id,))
            interests_data = c.fetchall()
            interests = [cls(*interest) for interest in interests_data]
            return interests
    
    @classmethod
    def get_by_name(cls, name, user_id):
        with sqlite3.connect('database.db') as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM interests WHERE name = ? AND user_id = ?", (name, user_id))
            interest_data = c.fetchone()
            if interest_data:
                return cls(*interest_data)
            return None

class ProfilePicture:
    def __init__(self, id=None, image_path=None, is_profile_picture=False, user_id=None):
        self.id = id
        self.image_path = image_path
        self.is_profile_picture = is_profile_picture
        self.user_id = user_id
        
    def save(self):
        with sqlite3.connect('database.db') as conn:
            c = conn.cursor()
            c.execute("INSERT INTO profile_pictures (image_path, is_profile_picture, user_id) VALUES (?, ?, ?)",
                      (self.image_path, self.is_profile_picture, self.user_id))
            self.id = c.lastrowid
            conn.commit()
        
    def delete(self):
        with sqlite3.connect('database.db') as conn:
            c = conn.cursor()
            c.execute("DELETE FROM profile_pictures WHERE id = ?", (self.id,))
            conn.commit()
    
    def to_dict(self):
        return {
            'id': self.id,
            'image_path': self.image_path,
            'is_profile_picture': self.is_profile_picture,
            'user_id': self.user_id
        }
    
    @classmethod
    def get_by_id(cls, photo_id):
        with sqlite3.connect('database.db') as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM profile_pictures WHERE id = ?", (photo_id,))
            photo_data = c.fetchone()
            if photo_data:
                return cls(*photo_data)
            return None

    @classmethod
    def get_by_user_id(cls, user_id):
        with sqlite3.connect('database.db') as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM profile_pictures WHERE user_id = ?", (user_id,))
            profile_pictures_data = c.fetchall()
            profile_pictures = [cls(*picture) for picture in profile_pictures_data]
            return profile_pictures

    @classmethod
    def get_profile_picture(cls, user_id):
        with sqlite3.connect('database.db') as conn:
            c = conn.cursor()
            c.execute("SELECT image_path FROM profile_pictures WHERE user_id = ? AND is_profile_picture = 1", (user_id,))
            profile_picture = c.fetchone()
            if profile_picture:
                return  profile_picture[0]
            else:
                return "../../static/assets/defaultpic.jpeg"


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