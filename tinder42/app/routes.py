import sqlite3
import secrets
from flask import Blueprint, render_template, url_for, flash, redirect, request,session
from app.forms import RegistrationForm, LoginForm
from app.models import User
from werkzeug.security import generate_password_hash, check_password_hash
from app.database import get_user_by_id, list_users, get_user_by_vertification_token
from config import Config
from itsdangerous import URLSafeTimedSerializer
from app.utils.mailservice import send_password_reset_email, send_verify_email


main = Blueprint('main', __name__)

def clear_flashes():
    if '_flashes' in session:
        session.pop('_flashes')

def flash_message(message, category):
    clear_flashes()  # Mevcut flash mesajlarını temizle
    flash(message, category)  # Yeni mesajı flash'la

@main.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'user_id' in session:
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        # Extract form data including new fields
        email = request.form.get('email')
        username = request.form.get('username')
        last_name = request.form.get('last_name')
        first_name = request.form.get('first_name')
        password = request.form.get('password')
        confirm_password = request.form.get('confirmpassword')
        gender = request.form.get('gender')
        birthday = request.form.get('birthday')
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        sexual_preferences = request.form.get('sexual_preferences')
        biography = request.form.get('biography')
        selected_interests = request.form.getlist('interests')

        # Instantiate the form with extracted data
        form = RegistrationForm(email, username, last_name, first_name, password, confirm_password, gender, birthday, latitude, longitude, sexual_preferences, biography, selected_interests)

        if form.validate():
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

            verification_token = secrets.token_urlsafe()
            # Assuming User model and database setup is correct
            new_user = User(email=email, username=username, last_name=last_name, first_name=first_name, password=hashed_password, gender=gender, birthday=birthday, latitude=latitude, longitude=longitude, sexual_preferences=sexual_preferences, biography=biography, verification_token=verification_token, verify_email=0)

            send_verify_email(new_user.email, url_for('main.verify_email', token=verification_token, _external=True), new_user.first_name, new_user.username)
            # Database insertion logic for user including new fields
            conn = sqlite3.connect(Config.DATABASE_URL)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (email, username, last_name, first_name, password, gender, birthday, latitude, longitude, sexual_preferences, biography, verification_token, verify_email) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                           (new_user.email, new_user.username, new_user.last_name, new_user.first_name, new_user.password, new_user.gender, new_user.birthday, new_user.latitude, new_user.longitude, new_user.sexual_preferences, new_user.biography, new_user.verification_token, new_user.verify_email))
            user_id = cursor.lastrowid

            # Database insertion logic for user interests
            for interest in selected_interests:
                cursor.execute("INSERT INTO interests (name, user_id) VALUES (?, ?)", (interest, user_id))
            
            conn.commit()
            conn.close()

            flash_message('Account created successfully! Please verify your email address.', 'success')
            return redirect(url_for('main.login'))
    else:
        form = RegistrationForm('', '', '', '', '', '', '', '', '', '', '', '', '')  # Empty form for GET request
    return render_template('signup.html', title='Sign up', form=form)

@main.route('/', methods=['GET', 'POST'])
@main.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('main.home'))
    conn = sqlite3.connect(Config.DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    # Sonuçları terminale yazdır
    for user in users:
        print(user)
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        form = LoginForm(email, password)
        if form.validate():
            conn = sqlite3.connect(Config.DATABASE_URL)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (form.email,))
            user = cursor.fetchone()
            conn.close()
            if user and check_password_hash(user[5], form.password):  # Assuming password is the 5th column in the users table
                if user[14] == 0:
                    flash_message('Please verify your email address.', 'info')
                    return redirect(url_for('main.login'))
                flash_message('Login successful!', 'success')
                session['user_id'] = user[0] 
                return redirect(url_for('main.home'))
            else:
                flash_message('Invalid email or password.', 'error')
    else:
        form = LoginForm('', '')  # Empty form for GET request
    return render_template('login.html', title='Login', form=form)

@main.route('/logout')
def logout():
    session.pop('user_id', None)
    flash_message('You have been logged out.', 'info')
    return redirect(url_for('main.login'))

@main.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    user_id = session.get('user_id')  # Kullanıcı ID'sini session'dan alın
    if user_id:
        user_data = get_user_by_id(user_id)  # Veritabanından kullanıcı bilgilerini çekin
        if not user_data.get('sexual_preferences') or not user_data.get('biography'):
            # Kullanıcı bilgilerini şablona argüman olarak geçirin
            flash_message('You have not completed your profile yet.', 'info')
            return render_template('home.html', title="Home", user=user_data, incomplete_profile=True) 
        if user_data:
            # Kullanıcı bilgilerini şablona argüman olarak geçirin
            return render_template('home.html', title="Home", user=user_data, incomplete_profile=False)
    # Eğer kullanıcı bilgisi bulunamazsa veya kullanıcı giriş yapmamışsa, hata mesajı gösterin
    return 'User not found or not logged in', 404

@main.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        conn = sqlite3.connect(Config.DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()
        if user:
            serializer = URLSafeTimedSerializer(Config.SECRET_KEY)
            token = serializer.dumps(user[0], salt=Config.PASSWORD_RESET_SALT)
            reset_url = url_for('main.change_password', token=token, _external=True, token_expires=int(time.time()) + 3600)
            send_password_reset_email(email, reset_url, user[5], user[3])
            flash_message('Password reset link has been sent to your email.', 'success')
            return redirect(url_for('main.login'))
        else:
            flash_message('Email not found.', 'error')
    return render_template('forgot-password.html', title='Forgot Password')

@main.route('/change-password/<token>', methods=['GET', 'POST'])
def change_password(token):
    if 'token_expires' in request.args:
        token_expires = request.args['token_expires']
        if int(token_expires) < int(time.time()):
            flash_message('The password reset link has expired.', 'error')
            return redirect(url_for('main.forgot_password'))

    if request.method == 'POST':
        new_password = request.form['password']
        confirm_password = request.form['confirmpassword']
        if new_password != confirm_password:
            flash_message('Passwords do not match.', 'error')
            return redirect(url_for('main.change_password', token=token))
        try:
            serializer = URLSafeTimedSerializer(Config.SECRET_KEY)
            user_id = serializer.loads(token, salt=Config.PASSWORD_RESET_SALT, max_age=3600)
            conn = sqlite3.connect(Config.DATABASE_URL)
            cursor = conn.cursor()
            hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')
            cursor.execute("UPDATE users SET password = ? WHERE id = ?", (hashed_password, user_id))
            conn.commit()
            conn.close()
            flash_message('Password has been changed successfully.', 'success')
            return redirect(url_for('main.login'))
        except:
            flash_message('The password reset link is invalid or has expired.', 'error')
            return redirect(url_for('main.forgot_password'))
    else:
        try:
            serializer = URLSafeTimedSerializer(Config.SECRET_KEY)
            email = serializer.loads(token, salt=Config.PASSWORD_RESET_SALT, max_age=3600)
            return render_template('change-password.html', title='Reset Password')
        except:
            flash_message('The password reset link is invalid or has expired.', 'error')
            return redirect(url_for('main.forgot_password'))
        
@main.route('/verify-email/<token>')
def verify_email(token):
    try:
        conn = sqlite3.connect(Config.DATABASE_URL)
        cursor = conn.cursor()
        user_data = get_user_by_vertification_token(token)
        if user_data['verification_token'] != token:
            flash_message('The email verification link is invalid or has expired.', 'error')
            return render_template('verify-failed.html', title='Verify Failed')
        user_id = user_data['id']
        cursor.execute("UPDATE users SET verify_email = 1 WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()
        session['user_id'] = user_id
        flash_message('Email verified successfully!', 'success')
        return redirect(url_for('main.home'))
    except:
        flash_message('The email verification link is invalid or has expired.', 'error')
        return render_template('verify-failed.html', title='Verify Failed')