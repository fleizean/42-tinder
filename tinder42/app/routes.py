import sqlite3
import secrets
from flask import Blueprint, render_template, url_for, flash, redirect, request,session, send_from_directory, jsonify
from app.forms import RegistrationForm, LoginForm
from app.models import User, Interest, ProfilePicture
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from itsdangerous import URLSafeTimedSerializer
import time
from app.utils.mailservice import send_password_reset_email, send_verify_email
from app.utils.utils import calculate_age, find_place
import os

main = Blueprint('main', __name__)

def clear_flashes():
    if '_flashes' in session:
        session.pop('_flashes')

def flash_message(message, category):
    clear_flashes()  # Mevcut flash mesajlarını temizle
    flash(message, category)  # Yeni mesajı flash'la

@main.route('/media/<path:filename>')
def media_files(filename):
    return send_from_directory('media', filename)

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
        picture = request.files.get('picture')

        # Instantiate the form with extracted data
        form = RegistrationForm(email, username, last_name, first_name, password, confirm_password, gender, birthday, latitude, longitude, sexual_preferences, biography, selected_interests, picture)

        if form.validate():
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

            verification_token = secrets.token_urlsafe()
            # Assuming User model and database setup is correct
            new_user = User(
                id=None,
                email=email,
                username=username,
                last_name=last_name,
                first_name=first_name,
                password=hashed_password,
                gender=gender,
                birthday=birthday,
                latitude=latitude,
                longitude=longitude,
                sexual_preferences=sexual_preferences,
                biography=biography,
                verification_token=verification_token,
                verify_email=0,
                fame_rating=0,
                comment_count=0,
                match_count=0,
                created_at=None,
                updated_at=None
            )

            send_verify_email(new_user.email, url_for('main.verify_email', token=verification_token, _external=True), new_user.first_name, new_user.username)

            conn = sqlite3.connect(Config.DATABASE_URL)
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO users (email, username, last_name, first_name, password, gender, birthday, latitude, longitude, sexual_preferences, biography, verification_token, verify_email, fame_rating, comment_count, match_count, created_at, updated_at) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (new_user.email, new_user.username, new_user.last_name, new_user.first_name, new_user.password, new_user.gender, new_user.birthday, new_user.latitude, new_user.longitude, new_user.sexual_preferences, new_user.biography, new_user.verification_token, new_user.verify_email, new_user.fame_rating, new_user.comment_count, new_user.match_count, new_user.created_at, new_user.updated_at))
            user_id = cursor.lastrowid

            for interest in selected_interests:
                cursor.execute("INSERT INTO interests (name, user_id) VALUES (?, ?)", (interest, user_id))
            
            # Save the uploaded picture
            if picture:
                media_dir = os.path.join('app', 'media')
                if not os.path.exists(media_dir):
                    os.makedirs(media_dir)
                picture_path = os.path.join(media_dir, f'{user_id}.jpg')
                picture.save(picture_path)
                
                cursor.execute('''INSERT INTO profile_pictures (image_path, is_profile_picture, user_id)
                                  VALUES (?, ?, ?)''', (f'{user_id}.jpg', True, user_id))

            conn.commit()
            conn.close()

            flash_message('Account created successfully! Please verify your email address.', 'success')
            return redirect(url_for('main.login'))
    else:
        form = RegistrationForm('', '', '', '', '', '', '', '', '', '', '', '', '', '')
    return render_template('signup.html', title='Sign up', form=form)

@main.route('/', methods=['GET', 'POST'])
@main.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        form = LoginForm(email, password)
        if form.validate():
            user = User.get_by_email(form.email)
            if user and check_password_hash(user.password, form.password):
                if user.verify_email == 0:
                    flash('Please verify your email address.', 'info')
                    return redirect(url_for('main.login'))
                flash('Login successful!', 'success')
                session['user_id'] = user.id
                return redirect(url_for('main.home'))
            else:
                flash('Invalid email or password.', 'error')
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
        return redirect(url_for('main.logout'))
    user_id = session.get('user_id')
    if user_id:
        user = User.get_by_id(user_id)
        if user:
            requested_profile_pic = ProfilePicture.get_profile_picture(user_id)
            if not user.sexual_preferences or not user.biography:
                flash_message('You have not completed your profile yet.', 'info')
                return render_template('home.html', title="Home", user=user, incomplete_profile=True, requested_profile_pic=requested_profile_pic)
            return render_template('home.html', title="Home", user=user, incomplete_profile=False, requested_profile_pic=requested_profile_pic)
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
        user_data = User.get_by_verification_token(token)
        if user_data.verification_token != token:
            flash_message('The email verification link is invalid or has expired.', 'error')
            return render_template('verify-failed.html', title='Verify Failed')
        user_id = user_data.id
        cursor.execute("UPDATE users SET verify_email = 1 WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()
        session['user_id'] = user_id
        flash_message('Email verified successfully!', 'success')
        return redirect(url_for('main.home'))
    except:
        flash_message('The email verification link is invalid or has expired.', 'error')
        return render_template('verify-failed.html', title='Verify Failed')

@main.route('/profile/<string:username>')
def profile(username):
    if 'user_id' not in session:
        return redirect(url_for('main.logout'))
    user_id = session.get('user_id')
    requested_user_data = User.get_by_id(user_id)
    profile_user_data = User.get_by_username(username)
    if not profile_user_data:
        return render_template('404.html', title='404')

    age = calculate_age(profile_user_data.birthday)
    place = find_place(profile_user_data.latitude, profile_user_data.longitude)
    interests = Interest.get_by_user_id(profile_user_data.id)

    requested_profile_pic = ProfilePicture.get_profile_picture(user_id)

    return render_template('profile.html', title='Profile', user=requested_user_data, profile_user=profile_user_data, age=age, place=place, interests=interests, requested_profile_pic=requested_profile_pic)

@main.route('/add_interest', methods=['POST'])
def add_interest():
    if 'user_id' not in session:
        return redirect(url_for('main.logout'))
    
    user_id = session.get('user_id')
    current_user = User.get_by_id(user_id)
    data = request.get_json()
    interest_name = data.get('interest')
    
    if interest_name:
        # Yeni ilgi alanını oluştur ve veritabanına ekle
        new_interest = Interest(name=interest_name, user_id=current_user.id)
        new_interest.save()
        
        return jsonify({'message': 'Interest added successfully'}), 200
    
    return jsonify({'message': 'Invalid interest'}), 400

@main.route('/delete_interest/<string:interest>', methods=['POST'])
def delete_interest(interest):
    if 'user_id' not in session:
        return redirect(url_for('main.logout'))
    
    user_id = session.get('user_id')
    print(session)
    current_user = User.get_by_id(user_id)
    print(interest)
    print("user_id")
    print(user_id)
    # İlgili ilgi alanını veritabanından sil
    interest = Interest.get_by_name(interest, user_id)
    if interest:
        interest.delete()
        return jsonify({'message': 'Interest deleted successfully'}), 200

    
    return jsonify({'message': 'Interest deleted successfully'}), 200

@main.route('/profile-settings/<string:username>', methods=['GET', 'POST'])
def profile_settings(username):
    if 'user_id' not in session:
        return redirect(url_for('main.logout'))

    user_id = session.get('user_id')
    requested_user_data = User.get_by_id(user_id)

    if requested_user_data.username != username:
        return render_template('404.html', title='404')

    if request.method == 'POST':
        conn = sqlite3.connect(Config.DATABASE_URL)
        # Form'dan gelen güncellemeleri işle
        email = request.form.get('email')
        username = request.form.get('username')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        password = request.form.get('password')
        gender = request.form.get('gender')
        sexual_preferences = request.form.get('sexual_preferences')
        biography = request.form.get('biography')
        birthday = request.form.get('birthday')
        new_interest_name = request.form.get('interest')

        # Güncellemeleri yap
        current_user.email = email
        current_user.username = username
        current_user.first_name = first_name
        current_user.last_name = last_name
        if password:
            current_user.password = password  # Şifreyi hashleyerek kaydet
        current_user.gender = gender
        current_user.sexual_preferences = sexual_preferences
        current_user.biography = biography
        current_user.birthday = birthday

        if new_interest_name:
            new_interest = Interest(id=None, name=new_interest_name, user_id=current_user.id)
            new_interest.save()

        # Veritabanında güncelle
        with sqlite3.connect('database.db') as conn:
            c = conn.cursor()
            c.execute("""
                UPDATE users SET email = ?, username = ?, first_name = ?, last_name = ?, password = ?, gender = ?, 
                sexual_preferences = ?, biography = ?, birthday = ? WHERE id = ?
            """, (current_user.email, current_user.username, current_user.first_name, current_user.last_name, 
                  current_user.password, current_user.gender, current_user.sexual_preferences, 
                  current_user.biography, current_user.birthday, current_user.id))
            conn.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile_settings', username=username))

    interests = [interest.name for interest in requested_user_data.interests]

    return render_template('profile-settings.html', title='Profile Settings', user=requested_user_data.to_dict(), interests=interests, username=username)


@main.route('/search', methods=['GET', 'POST'])
def search():
    if 'user_id' not in session:
        return redirect(url_for('main.logout'))
    user_id = session.get('user_id')
    user_data = User.get_by_id(user_id)
    search_query = request.args.get('query', '')
    selected_interests = request.args.getlist('interests')
    search_results = []

    if search_query or selected_interests:
        search_results = User.search_users(search_query, selected_interests)
    requested_profile_pic = ProfilePicture.get_profile_picture(user_id)
    for user in search_results: # data düzgün şekilde geliyor search tarafına işlenmesi kaldı 
        print(user.username)
    return render_template('search.html', title='Search', user=user_data, search_results=search_results, search_query=search_query, requested_profile_pic=requested_profile_pic)