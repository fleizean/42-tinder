import os
from dotenv import load_dotenv
from pathlib import Path
import requests
import time
from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import random
import glob
from app.models.user import User
from app.models.profile import Profile, Gender, SexualPreference, Tag, ProfilePicture
from app.core.config import settings

# Load .env file
load_dotenv()

# Add the parent directory to Python path so we can import from app
MEDIA_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "media")


fake = Faker(['tr_TR'])

# Database connection using env variable
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()


# Örnek tag listesi
SAMPLE_TAGS = [
    "seyahat", "spor", "müzik", "sinema", "kitap", "yemek", "dans", 
    "fotoğraf", "yoga", "doğa", "kamp", "kahve", "teknoloji", "sanat",
    "tiyatro", "konser", "bisiklet", "koşu", "yüzme", "futbol"
]

# Örnek biyografiler
BIO_TEMPLATES = [
    "{}. {} için buradayım.",
    "Hayatta en çok sevdiğim şey {}. {} konusunda tutkulum var.",
    "{} ve {} ile ilgileniyorum.",
    "Boş zamanlarımda {} yapmayı seviyorum. {} ile aram çok iyi.",
]

def get_existing_profile_pictures():
    """Find all existing profile pictures in the media directory"""
    pictures_dir = os.path.join(MEDIA_ROOT, "profile_pictures")
    
    # Check if directory exists
    if not os.path.exists(pictures_dir):
        print(f"Warning: Directory {pictures_dir} does not exist")
        return []
    
    # Get all directories containing pictures
    profile_dirs = [d for d in os.listdir(pictures_dir) 
                    if os.path.isdir(os.path.join(pictures_dir, d))]
    
    # Dictionary to store profile IDs and their picture paths
    profile_pictures = {}
    
    for profile_dir in profile_dirs:
        full_dir_path = os.path.join(pictures_dir, profile_dir)
        # Find all image files in the directory
        image_files = []
        for ext in ['*.jpg', '*.jpeg', '*.png']:
            image_files.extend(glob.glob(os.path.join(full_dir_path, ext)))
        
        if image_files:
            profile_pictures[profile_dir] = [os.path.basename(img) for img in image_files]
    
    return profile_pictures

def use_existing_profile_picture(profile_id, profile_pictures_dict):
    """Assign an existing profile picture to a new profile"""
    # If there are no profile directories with pictures, return False
    if not profile_pictures_dict:
        print("No existing profile pictures found")
        return False
    
    # Get a random profile ID from the existing ones
    source_profile_id = random.choice(list(profile_pictures_dict.keys()))
    
    # Get all pictures for this profile
    pictures = profile_pictures_dict[source_profile_id]
    
    if not pictures:
        return False
    
    # Create directory for the new profile if it doesn't exist
    profile_dir = os.path.join(MEDIA_ROOT, "profile_pictures", profile_id)
    Path(profile_dir).mkdir(parents=True, exist_ok=True)
    
    # Copy up to 3 random pictures (or all if less than 3)
    num_pics = min(len(pictures), random.randint(1, 3))
    selected_pics = random.sample(pictures, num_pics)
    
    source_dir = os.path.join(MEDIA_ROOT, "profile_pictures", source_profile_id)
    copied_files = []
    
    for i, pic_name in enumerate(selected_pics):
        source_path = os.path.join(source_dir, pic_name)
        dest_name = f"{i+1}{os.path.splitext(pic_name)[1]}"  # 1.jpg, 2.jpg, etc.
        dest_path = os.path.join(profile_dir, dest_name)
        
        # Copy the file
        try:
            with open(source_path, 'rb') as src_file:
                with open(dest_path, 'wb') as dest_file:
                    dest_file.write(src_file.read())
            copied_files.append(dest_name)
            print(f"Copied image {pic_name} to {profile_id}/{dest_name}")
        except Exception as e:
            print(f"Error copying image {pic_name}: {str(e)}")
    
    return copied_files

def remove_turkish_chars(text):
    """
    Türkçe karakterleri İngilizce karşılıklarına dönüştürür
    ç -> c, ı -> i, ğ -> g, ş -> s, ö -> o, ü -> u
    """
    replacements = {
        'ç': 'c', 'Ç': 'C',
        'ı': 'i', 'İ': 'I',
        'ğ': 'g', 'Ğ': 'G',
        'ş': 's', 'Ş': 'S',
        'ö': 'o', 'Ö': 'O',
        'ü': 'u', 'Ü': 'U'
    }
    
    for tr_char, en_char in replacements.items():
        text = text.replace(tr_char, en_char)
    
    return text

def create_fake_users(count=50):
    # Get existing profile pictures
    existing_profile_pictures = get_existing_profile_pictures()
    
    users = []
    for _ in range(count):
        # Temel kullanıcı bilgileri
        first_name = fake.first_name()
        last_name = fake.last_name()

        first_name_safe = remove_turkish_chars(first_name)
        #last_name_safe = remove_turkish_chars(last_name)

        username = f"{first_name_safe.lower()}_{fake.random_number(digits=4)}"
        email = f"{username}@{fake.domain_name()}"
        password = "password123"  # Tüm test kullanıcıları için aynı şifre
        
        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            hashed_password=User.get_password_hash(password),
            is_active=True,
            is_verified=True,
            created_at=datetime.utcnow(),
            last_login=datetime.utcnow() - timedelta(minutes=random.randint(1, 1440)),
            is_online=random.choice([True, False]),
            last_online=datetime.utcnow() - timedelta(minutes=random.randint(1, 1440))
        )
        
        db.add(user)
        db.flush()  # ID'yi almak için flush
        
        # Kullanıcı profili
        profile = Profile(
            id=str(fake.uuid4()),
            user_id=user.id,
            gender=random.choice(list(Gender)),
            sexual_preference=random.choice(list(SexualPreference)),
            biography=random.choice(BIO_TEMPLATES).format(
                random.choice(SAMPLE_TAGS),
                random.choice(SAMPLE_TAGS)
            ),
            latitude=float(fake.latitude()),
            longitude=float(fake.longitude()),
            fame_rating=random.uniform(0, 5),
            is_complete=True,
            birth_date=fake.date_of_birth(minimum_age=18, maximum_age=50)
        )
        
        db.add(profile)
        
        # Use existing profile pictures
        copied_pics = use_existing_profile_picture(profile.id, existing_profile_pictures)
        
        if copied_pics:
            for i, pic_name in enumerate(copied_pics):
                # Add to database
                picture = ProfilePicture(
                    profile_id=profile.id,
                    file_path=f"profile_pictures/{profile.id}/{pic_name}",
                    backend_url=f"{settings.BACKEND_URL}/media/profile_pictures/{profile.id}/{pic_name}",
                    is_primary=i == 0
                )
                db.add(picture)
        
        # Etiketler
        profile_tags = random.sample(SAMPLE_TAGS, random.randint(2, 5))
        for tag_name in profile_tags:
            tag = db.query(Tag).filter(Tag.name == tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
                db.flush()
            profile.tags.append(tag)
        
        users.append(user)
        
    try:
        db.commit()
        print(f"{count} fake kullanıcı başarıyla oluşturuldu!")
    except Exception as e:
        db.rollback()
        print(f"Hata: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_fake_users(200)  # 200 sahte kullanıcı oluştur