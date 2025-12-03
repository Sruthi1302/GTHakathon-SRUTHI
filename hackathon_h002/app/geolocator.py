import math
from typing import List, Dict, Optional


def haversine_distance(lat1, lon1, lat2, lon2):
    """Approximate distance between two geo points in meters."""
    R = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def find_nearest_store(user_lat: float, user_lon: float, stores: List[Dict]) -> Optional[Dict]:
    """Return nearest store with distance_in_m."""
    best_store = None
    best_dist = None

    for store in stores:
        try:
            dist = haversine_distance(
                float(store["latitude"]),
                float(store["longitude"]),
                float(user_lat),
                float(user_lon)
            )
        except Exception:
            continue

        if best_dist is None or dist < best_dist:
            best_dist = dist
            best_store = {**store}
            best_store["distance_in_m"] = round(dist, 1)

    return best_store
