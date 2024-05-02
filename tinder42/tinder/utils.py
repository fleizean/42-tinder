import asyncio, os, hashlib
from django.utils.crypto import get_random_string
from django.core.files.base import ContentFile
from django.core.cache import cache

def delete_from_media(path):
    if os.path.isfile(path):
        os.remove(path)

def get_upload_to(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s_%s.%s" % (instance.username, get_random_string(length=7), ext)
    return filename