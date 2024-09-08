from datetime import datetime
import sqlite3

class User:
    def __init__(self, id, email, username, last_name, first_name, password, gender, sexual_preferences, biography, fame_rating, comment_count, match_count, latitude, longitude, birthday, verification_token, verify_email, created_at, updated_at, profile_pictures=None, interests=None):
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

    @classmethod
    def get_by_id(cls, user_id):
        with sqlite3.connect('database.db') as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user_data = c.fetchone()
            print(user_data)
            if user_data:
                user = cls(*user_data)
                user.profile_pictures = ProfilePicture.get_by_user_id(user_id)
                user.interests = Interest.get_by_user_id(user_id)
                print(user.sexual_preferences)
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
                return user
            return None
    
    @classmethod
    def search_users(cls, query, interests):
        with sqlite3.connect('database.db') as conn:
            c = conn.cursor()
            search_query = f"%{query}%"
            if query and interests:
                interests_placeholders = ','.join('?' for _ in interests)
                c.execute(f"""
                    SELECT DISTINCT u.* FROM users u
                    LEFT JOIN interests i ON u.id = i.user_id
                    WHERE (u.username LIKE ? OR u.first_name LIKE ? OR u.last_name LIKE ?)
                    AND i.name IN ({interests_placeholders})
                """, (search_query, search_query, search_query, *interests))
            elif query:
                c.execute("""
                    SELECT * FROM users 
                    WHERE username LIKE ? OR first_name LIKE ? OR last_name LIKE ?
                """, (search_query, search_query, search_query))
            elif interests:
                interests_placeholders = ','.join('?' for _ in interests)
                c.execute(f"""
                    SELECT DISTINCT u.* FROM users u
                    LEFT JOIN interests i ON u.id = i.user_id
                    WHERE i.name IN ({interests_placeholders})
                """, (*interests,))
            
            users_data = c.fetchall()
            users_list = []
            
            for user_data in users_data:
                user = cls(*user_data)
                user.profile_pictures = ProfilePicture.get_by_user_id(user.id)
                user.interests = Interest.get_by_user_id(user.id)
                users_list.append(user)
            
            return users_list


class Interest:
    def __init__(self, id, name, user_id):
        self.id = id
        self.name = name
        self.user_id = user_id

    @classmethod
    def get_by_user_id(cls, user_id):
        with sqlite3.connect('database.db') as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM interests WHERE user_id = ?", (user_id,))
            interests_data = c.fetchall()
            interests = [cls(*interest) for interest in interests_data]
            return interests


class ProfilePicture:
    def __init__(self, id, image_path, is_profile_picture, user_id):
        self.id = id
        self.image_path = image_path
        self.is_profile_picture = is_profile_picture
        self.user_id = user_id

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
                return "/media/" + profile_picture[0]
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
