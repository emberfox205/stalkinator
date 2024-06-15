from libs.oauth_token_get import oauth_token_get
from libs.coords_get import coords_get
import time, socket
import threading

latest_token = None

def update_token():
    global latest_token
    while True:
        # Update the shared token value
        latest_token = oauth_token_get()
        #print(latest_token)
        time.sleep(250)

def get_coords():
    global latest_token
    while True:
        ipv4_address = socket.gethostbyname(socket.gethostname())
        #print("coord: ",latest_token)
        coords_get(access_token=latest_token, url=f"http://{ipv4_address}:8080/data")
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