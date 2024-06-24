import sqlite3
DATABASE = 'instance/stalkinator.db'
name, lat, lon, thing_id, distance = "hoa", 11.10682107321737 ,106.61549091339113, "0fdf49e8-cd4a-41a5-8a64-1b2442bee8de" , 20
conn = sqlite3.connect(DATABASE)
cur = conn.cursor()
cur.execute('INSERT INTO geofence (name, lat, lon, thing_id, distance) VALUES (?, ?, ?, ?, ?)', 
                        (name, lat, lon, thing_id, distance))
conn.commit()
conn.close()