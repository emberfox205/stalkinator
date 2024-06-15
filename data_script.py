from libs.oauth_token_get import oauth_token_get
from libs.coords_get import coords_get
import time, socket
import threading
import sqlite3

latest_token = None
def update_token():
    global latest_token
    while True:
        # Update the shared token value
        latest_token = oauth_token_get()
        #print(shared_token.value)
        time.sleep(250)

def get_coords():
    while True:
        connect = sqlite3.connect("instance/stalkinator.db")
        cur = connect.cursor()
        cur.execute("Select tid from user")
        connect.commit()
        values = set([row[0] for row in cur.fetchall()])
        for value in values:
            coords_get(access_token=latest_token, cur = cur, connect = connect ,thing_id = value)
        time.sleep(10)

if __name__ == "__main__":
    # Pass the shared latest_token to both functions
    t1 = threading.Thread(target=update_token)
    t2 = threading.Thread(target=get_coords)
    t1.start()
    while not latest_token:
        print("Waiting for token...")
        time.sleep(2)
    t2.start()
    t1.join()
    t2.join()