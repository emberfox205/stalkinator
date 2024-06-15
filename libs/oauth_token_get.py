from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv
import os

def oauth_token_get():
    load_dotenv()
    CLIENT_ID=os.getenv('CLIENT_ID')
    CLIENT_SECRET=os.getenv('CLIENT_SECRET')

    oauth_client = BackendApplicationClient(client_id=CLIENT_ID)
    token_url = "https://api2.arduino.cc/iot/v1/clients/token"

    oauth = OAuth2Session(client=oauth_client)
    token = oauth.fetch_token(
        token_url=token_url,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        include_client_id=True,
        audience="https://api2.arduino.cc/iot",
    )
    access_token = token.get("access_token")
    print("Got a token, expires in {} seconds".format(token.get("expires_in")))
    return access_token


if __name__ == "__main__":
    print(oauth_token_get())