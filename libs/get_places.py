import requests
import sqlite3
from dotenv import load_dotenv
import os

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

def save_places_to_db(places, thing_id):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    
    # Ensure the geofence table exists
    cur.execute('''CREATE TABLE IF NOT EXISTS geofence 
                   (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    name TEXT, 
                    lat REAL, 
                    lon REAL,
                    thing_id TEXT)''')
    
    # Check if data for the thing_id already exists
    cur.execute("SELECT COUNT(*) FROM geofence WHERE thing_id = ?", (thing_id,))
    count = cur.fetchone()[0]
    if count > 0:
        print(f"Data for thing_id {thing_id} already exists in the geofence table. Skipping insert.")
    else:
        for place in places:
            properties = place['properties']
            name = properties.get('name')
            lat = properties['lat']
            lon = properties['lon']
            cur.execute('INSERT INTO geofence (name, lat, lon, thing_id) VALUES (?, ?, ?, ?)', 
                        (name, lat, lon, thing_id))
    
    conn.commit()
    conn.close()

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
        save_places_to_db(places, user_thing_id)
        print(f"Processed places for thing_id {user_thing_id}.")
    else:
        print("No coordinates found for the provided thing_id.")
