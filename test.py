DATABASE = 'instance/stalkinator.db'
import sqlite3
conn = sqlite3.connect(DATABASE)
cur = conn.cursor()
name, lat, lon, thing_id, distance = ("hoa", 11.10691, 106.6148274,"9770356d-1259-48d6-a653-0ab4bde124e8" , 7)
cur.execute('INSERT INTO geofence (name, lat, lon, thing_id, distance) VALUES (?, ?, ?, ?, ?)', 
                        (name, lat, lon, thing_id, distance))
conn.commit()
conn.close()