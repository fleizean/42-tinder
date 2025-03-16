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

def download_ai_profile_picture(profile_id, index):
    """Download an AI-generated profile picture"""
    # Create directory if it doesn't exist
    profile_dir = os.path.join(MEDIA_ROOT, "profile_pictures", profile_id)
    Path(profile_dir).mkdir(parents=True, exist_ok=True)
    
    # Define file path
    file_name = f"{index+1}.jpg"
    file_path = os.path.join(profile_dir, file_name)
    
    try:
        # Get a random AI-generated face from thispersondoesnotexist.com
        # This site serves a new random face on each request
        response = requests.get('https://thispersondoesnotexist.com/', stream=True)
        
        if response.status_code == 200:
            # Save the image
            with open(file_path, 'wb') as f:
                f.write(response.content)
            print(f"Downloaded AI image for {profile_id}/{file_name}")
            return True
        else:
            print(f"Failed to download AI image: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error downloading AI image: {str(e)}")
        return False

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
        
        # Profil fotoğrafları
        for i in range(random.randint(1, 3)):
            # Download AI-generated photo
            success = download_ai_profile_picture(profile.id, i)
            
            # Only add to database if download was successful
            if success:
                picture = ProfilePicture(
                    profile_id=profile.id,
                    file_path=f"profile_pictures/{profile.id}/{i+1}.jpg",
                    backend_url=f"{settings.BACKEND_URL}/media/profile_pictures/{profile.id}/{i+1}.jpg",
                    is_primary=i == 0
                )
                db.add(picture)
            
            # Add a small delay to avoid overloading the service
            time.sleep(0.5)
        
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
    create_fake_users(200)  # 50 sahte kullanıcı oluştur