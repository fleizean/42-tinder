import sqlite3

from config import Config


def create_database():
    conn = sqlite3.connect(Config.DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        email TEXT NOT NULL UNIQUE,
                        username TEXT NOT NULL UNIQUE,
                        last_name TEXT NOT NULL,
                        first_name TEXT NOT NULL,
                        password TEXT NOT NULL,
                        gender TEXT,
                        sexual_preferences TEXT,
                        biography TEXT,
                        fame_rating INTEGER DEFAULT 0,
                        comment_count INTEGER DEFAULT 0,
                        match_count INTEGER DEFAULT 0,
                        latitude TEXT,
                        longitude TEXT,
                        birthday DATE,
                        verification_token TEXT,
                        verify_email BOOLEAN DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        online BOOLEAN DEFAULT 0,
                        last_online TIMESTAMP DEFAULT updated_at
                    )"""
    )
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS interests (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        user_id INTEGER NOT NULL,
                        FOREIGN KEY(user_id) REFERENCES users(id)
                    )"""
    )
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS profile_pictures (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        image_path TEXT NOT NULL,
                        is_profile_picture BOOLEAN NOT NULL,
                        FOREIGN KEY(user_id) REFERENCES users(id)
                    )"""
    )
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        sender_id INTEGER NOT NULL,
                        receiver_id INTEGER NOT NULL,
                        content TEXT NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY(sender_id) REFERENCES users(id),
                        FOREIGN KEY(receiver_id) REFERENCES users(id)
                    )"""
    )
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS likes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender_id INTEGER NOT NULL,
                    receiver_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY(sender_id) REFERENCES users(id),
                    FOREIGN KEY(receiver_id) REFERENCES users(id)
                )"""
    )
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS connections (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user1_id INTEGER NOT NULL,
                        user2_id INTEGER NOT NULL,
                        connected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY(user1_id) REFERENCES users(id),
                        FOREIGN KEY(user2_id) REFERENCES users(id),
                        CHECK (user1_id < user2_id)
                    )"""
    )
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS notifications (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        type TEXT NOT NULL,
                        message TEXT NOT NULL,
                        related_user_id INTEGER,
                        is_read BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY(user_id) REFERENCES users(id),
                        FOREIGN KEY(related_user_id) REFERENCES users(id)
                    )"""
    )
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS blocks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        blocker_id INTEGER NOT NULL,
                        blocked_id INTEGER NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY(blocker_id) REFERENCES users(id),
                        FOREIGN KEY(blocked_id) REFERENCES users(id)
                    )"""
    )

    conn.commit()
    conn.close()
