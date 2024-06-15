from libs.oauth_token_get import oauth_token_get
from libs.coords_get import coords_get
import time, socket
from multiprocessing import Process, Manager

manager = Manager()
latest_token = manager.Value('d', None)  # 'd' is the typecode for strings in this context

def update_token(shared_token):
    while True:
        # Update the shared token value
        shared_token.value = oauth_token_get()
        #print(shared_token.value)
        time.sleep(250)

def get_coords(shared_token):
    while True:
        ipv4_address = socket.gethostbyname(socket.gethostname())
        #print("coord: ",shared_token.value)
        coords_get(access_token=shared_token.value, url=f"http://{ipv4_address}:8080/data")
        time.sleep(10)

if __name__ == "__main__":
    # Pass the shared latest_token to both functions
    p1 = Process(target=update_token, args=(latest_token,))
    p2 = Process(target=get_coords, args=(latest_token,))
    p1.start()
    if not latest_token.value:
        print("Waiting for token...")
        time.sleep(2)
    p2.start()
    p1.join()
    p2.join()