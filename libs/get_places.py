import requests
import sqlite3
from dotenv import load_dotenv
import os
import math

load_dotenv()

API_KEY = os.getenv('GEOAPIFY_API_KEY')
DATABASE = 'instance/stalkinator.db'

def get_user_coords(thing_id):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute("SELECT lat, lon FROM Makers WHERE thing_id = ? ORDER BY time DESC LIMIT 1", (thing_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return row[0], row[1]
    else:
        return None, None

def fetch_places(lat, lon):
    url = "https://api.geoapify.com/v2/places"
    params = {
        "categories": "catering.bar,catering.pub",
        "filter": f"circle:{lon},{lat},30000",
        "limit": 20,
        "apiKey": API_KEY
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()['features']
    else:
        print(f"Error fetching data from Geoapify: {response.status_code}")
        return []


def save_places_to_db(places, thing_id, user_lat, user_lon):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()

    for place in places:
        properties = place['properties']
        name = properties.get('name') or "unknown"
        lat = properties['lat']
        lon = properties['lon']
        distance = haversine(user_lat, user_lon, lat, lon)
        
        # Check if the place already exists for the given thing_id
        cur.execute("SELECT id FROM geofence WHERE name = ? AND lat = ? AND lon = ? AND thing_id = ?", 
                    (name, lat, lon, thing_id))
        row = cur.fetchone()
        
        if row:
            # Update the distance if the place exists
            cur.execute("UPDATE geofence SET distance = ? WHERE id = ?", (distance, row[0]))
        else:
            # Insert the new place if it doesn't exist
            cur.execute('INSERT INTO geofence (name, lat, lon, thing_id, distance) VALUES (?, ?, ?, ?, ?)', 
                        (name, lat, lon, thing_id, distance))
    
    conn.commit()
    conn.close()

def haversine(lat1, lon1, lat2, lon2):
    # Radius of the Earth in kilometers
    R = 6371.0
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    return distance

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        user_thing_id = sys.argv[1]
    else:
        print("No thing_id provided.")
        sys.exit(1)
    
    lat, lon = get_user_coords(user_thing_id)
    if lat is not None and lon is not None:
        places = fetch_places(lat, lon)
        save_places_to_db(places, user_thing_id, lat, lon)
        print(f"Processed places for thing_id {user_thing_id}.")
    else:
        print("No coordinates found for the provided thing_id.")
