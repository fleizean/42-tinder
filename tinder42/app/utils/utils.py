from datetime import datetime
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

GEO_API_KEY = os.getenv('GEO_API_KEY')

def calculate_age(birthday):
    today = datetime.today()
    birthdate = datetime.strptime(birthday, '%Y-%m-%d')
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    return age

def find_place(longitude, latitude):
    url = f'https://us1.locationiq.com/v1/reverse?key={GEO_API_KEY}&lat={longitude}&lon={latitude}&format=json'
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        address = data.get('address', {})
        city = address.get('city', None)
        town = address.get('town', None)
        province = address.get('province', None)
        region = address.get('region', None)
        country = address.get('country', None)
        
        # Öncelik sırasına göre şehir bilgisini döndür
        if city:
            return city
        elif town:
            return town
        elif province:
            return province
        elif region:
            return region
        else:
            return country
    else:
        return 'Unknown.'