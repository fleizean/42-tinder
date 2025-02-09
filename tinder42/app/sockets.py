from app import socketio
from flask import session
from datetime import datetime
import sqlite3
from config import Config

@socketio.on('connect')
def handle_connect():
    if 'user_id' in session:
        user_id = session['user_id']
        with sqlite3.connect(Config.DATABASE_URL) as conn:
            c = conn.cursor()
            c.execute("UPDATE users SET online = 1 WHERE id = ?", (user_id,))
            conn.commit()

@socketio.on('disconnect')
def handle_disconnect():
    if 'user_id' in session:
        user_id = session['user_id']
        with sqlite3.connect(Config.DATABASE_URL) as conn:
            c = conn.cursor()
            c.execute("UPDATE users SET online = 0, last_online = ? WHERE id = ?", 
                     (datetime.now(), user_id))
            conn.commit()

@socketio.on('message')
def handle_message(data):
    sender_id = session.get('user_id')
    receiver_id = data['receiver_id']
    content = data['content']
    
    if not sender_id or not content:
        return
    
    # Save message to database
    with sqlite3.connect(Config.DATABASE_URL) as conn:
        c = conn.cursor()
        c.execute('''INSERT INTO messages (sender_id, receiver_id, content)
                     VALUES (?, ?, ?)''', (sender_id, receiver_id, content))
        conn.commit()
    
    # Emit to receiver
    socketio.emit('new_message', {
        'sender_id': sender_id,
        'content': content,
        'timestamp': datetime.now().isoformat()
    }, room=str(receiver_id))
    
    # Create notification
    c.execute('''INSERT INTO notifications (user_id, type, message, related_user_id)
                 VALUES (?, ?, ?, ?)''',
              (receiver_id, 'message', 'New message from user', sender_id))
    conn.commit()