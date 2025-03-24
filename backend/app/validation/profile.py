from datetime import datetime, timezone

def validate_gender(gender):
    valid_genders = ['male', 'female', 'non_binary', 'other']
    
    if gender not in valid_genders:
        return False, f"Gender must be one of: {', '.join(valid_genders)}"
    
    return True, ""

def validate_sexual_preference(preference):
    valid_preferences = ['heterosexual', 'homosexual', 'bisexual', 'other']
    
    if preference not in valid_preferences:
        return False, f"Sexual preference must be one of: {', '.join(valid_preferences)}"
    
    return True, ""

def validate_biography(bio):
    if bio and len(bio) > 1000:
        return False, "Biography must be less than 1000 characters"
    
    return True, ""

def validate_coordinates(lat, lon):
    # Check if latitude is within valid range (-90 to 90)
    if lat is not None and (lat < -90 or lat > 90):
        return False, "Latitude must be between -90 and 90"
    
    # Check if longitude is within valid range (-180 to 180)
    if lon is not None and (lon < -180 or lon > 180):
        return False, "Longitude must be between -180 and 180"
    
    return True, ""

def validate_birth_date(birth_date):
    if not birth_date:
        return True, ""  # Birth date is optional
    
    today = datetime.now(timezone.utc)
    
    try:
        # Convert string to datetime if needed
        if isinstance(birth_date, str):
            birth_date = datetime.fromisoformat(birth_date.replace('Z', '+00:00'))
        
        # Check if date is in future
        if birth_date > today:
            return False, "Birth date cannot be in the future"
        
        # Check minimum age (16)
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        if age < 16:
            return False, "Minimum age requirement is 16 years"
        
        # Check reasonable date range
        if birth_date.year < 1900:
            return False, "Please enter a valid birth date"
        
        # Check maximum age (70)
        if age > 70:
            return False, "Please enter a valid birth date"
        
    except ValueError:
        return False, "Invalid date format"
    
    return True, ""

def validate_tag(tag):
    BLACKLISTED_TAGS = [
        'admin', 'moderator', 'staff', 'support',
        'system', 'crushit', 'crushitapp'
    ]
    
    # Check length
    if len(tag) < 2 or len(tag) > 20:
        return False, "Tag name must be between 2 and 20 characters"
    
    # Check characters - only allow letters, numbers, and hyphens
    if not tag.replace('-', '').isalnum():
        return False, "Tag can only contain letters, numbers, and hyphens"
    
    # Check for valid hyphen usage
    if tag.startswith('-') or tag.endswith('-'):
        return False, "Tag cannot start or end with a hyphen"
    
    # Check for consecutive hyphens
    if '--' in tag:
        return False, "Tag cannot contain consecutive hyphens"
    
    # Check blacklist
    if tag.lower() in BLACKLISTED_TAGS:
        return False, f"'{tag}' tag is not allowed"
    
    # Check if tag contains only hyphens
    if all(c == '-' for c in tag):
        return False, "Tag cannot consist only of hyphens"
    
    return True, ""

def validate_tags(tags):
    if not tags:
        return True, ""  # Tags are optional
    
    errors = []
    for tag in tags:
        is_valid, msg = validate_tag(tag)
        if not is_valid:
            errors.append(f"Tag '{tag}': {msg}")
    
    if errors:
        return False, errors
    
    return True, ""

def validate_profile_update(data):
    errors = {}
    
    # Validate gender if provided
    if "gender" in data:
        is_valid, msg = validate_gender(data.get("gender"))
        if not is_valid:
            errors["gender"] = msg
    
    # Validate sexual preference if provided
    if "sexual_preference" in data:
        is_valid, msg = validate_sexual_preference(data.get("sexual_preference"))
        if not is_valid:
            errors["sexual_preference"] = msg
    
    # Validate biography if provided
    if "biography" in data:
        is_valid, msg = validate_biography(data.get("biography"))
        if not is_valid:
            errors["biography"] = msg
    
    # Validate coordinates if provided
    if "latitude" in data or "longitude" in data:
        lat = data.get("latitude")
        lon = data.get("longitude")
        is_valid, msg = validate_coordinates(lat, lon)
        if not is_valid:
            errors["coordinates"] = msg
    
    # Validate birth date if provided
    if "birth_date" in data:
        is_valid, msg = validate_birth_date(data.get("birth_date"))
        if not is_valid:
            errors["birth_date"] = msg
    
    return len(errors) == 0, errors