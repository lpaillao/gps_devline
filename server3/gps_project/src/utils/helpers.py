import math

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in kilometers

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return R * c

def get_heading(angle):
    headings = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    return headings[round(angle / 45) % 8]

def get_movement_status(speed):
    if speed == 0:
        return "Stopped"
    elif speed < 10:
        return "Idle"
    elif speed < 60:
        return "Moving"
    else:
        return "Fast Moving"