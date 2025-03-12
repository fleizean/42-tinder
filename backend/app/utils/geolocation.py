from math import radians, cos, sin, asin, sqrt
from typing import Tuple, Optional

def haversine_distance(
    lat1: float, 
    lon1: float, 
    lat2: float, 
    lon2: float
) -> float:
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    
    Returns:
        Distance in kilometers
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers
    
    return c * r

def get_bounding_box(
    lat: float, 
    lon: float, 
    distance_km: float
) -> Tuple[float, float, float, float]:
    """
    Calculate a bounding box around a point with a given radius in kilometers
    
    Returns:
        min_lat, min_lon, max_lat, max_lon
    """
    # Approximate conversion from kilometers to degrees
    # 1 degree latitude is approximately 111 km
    lat_change = distance_km / 111.0
    
    # 1 degree longitude varies with latitude
    # At the equator it's also about 111 km, but shrinks with cos(lat)
    lon_change = distance_km / (111.0 * cos(radians(lat)))
    
    min_lat = lat - lat_change
    max_lat = lat + lat_change
    min_lon = lon - lon_change
    max_lon = lon + lon_change
    
    return min_lat, min_lon, max_lat, max_lon