import json
import os
import requests
import sqlite3
import math

DATAFILE = "data.json"
DISTANCE_THRESHOLD = 20000

def read_latest_coords():
    if not os.path.isfile(DATAFILE):
        raise FileNotFoundError(f"{DATAFILE} does not exist.")

    with open(DATAFILE, "r") as file:
        markers = json.load(file)

    if not markers:
        raise ValueError("No markers found in data.json.")

    latest_marker = markers[-1]
    return float(latest_marker["lat"]), float(latest_marker["lon"])

def fetch_places(lat, lon, api_key):
    url = "https://api.geoapify.com/v2/places"
    params = {
        "categories": "catering.bar,catering.pub",
        "filter": f"circle:{lon},{lat},50000",
        "limit": 50,
        "apiKey": api_key
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()["features"]

def init_db():
    conn = sqlite3.connect('places.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS places
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, lat REAL, lon REAL, distance REAL)''')
    conn.commit()
    return conn

def save_places_to_db(conn, places, user_lat, user_lon):
    cursor = conn.cursor()
    for place in places:
        place_lat = float(place["geometry"]["coordinates"][1])
        place_lon = float(place["geometry"]["coordinates"][0])
        distance = haversine(user_lat, user_lon, place_lat, place_lon)
        cursor.execute("INSERT INTO places (lat, lon, distance) VALUES (?, ?, ?)", (place_lat, place_lon, distance))
    conn.commit()

def fetch_and_store_places(markers):
    GEOAPIFY_API_KEY = os.getenv('GEOAPIFY_API_KEY')
    
    if not GEOAPIFY_API_KEY:
        raise ValueError("Geoapify API key not found")
    conn = init_db()

    if should_fetch_new_places(conn, markers):
        clear_places_db(conn)
        user_lat, user_lon = read_latest_coords()
        places = fetch_places(user_lat, user_lon, GEOAPIFY_API_KEY)
        save_places_to_db(conn, places, user_lat, user_lon)
    conn.close()

def should_fetch_new_places(conn, markers):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM places")
    count = cursor.fetchone()[0]
    if count == 0:
        return True
    total_distance = calculate_total_distance(markers)
    if total_distance > DISTANCE_THRESHOLD:
        return True
    return False

def clear_places_db(conn):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM places")
    conn.commit()

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def calculate_total_distance(markers):
    if len(markers) < 2:
        return 0
    total_distance = 0
    for i in range(1, len(markers)):
        total_distance += haversine(
            float(markers[i-1]["lat"]), float(markers[i-1]["lon"]),
            float(markers[i]["lat"]), float(markers[i]["lon"])
        )
    return total_distance
