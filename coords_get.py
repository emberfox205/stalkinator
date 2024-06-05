# Successful
import iot_api_client as iot
from iot_api_client.rest import ApiException
from iot_api_client.configuration import Configuration
import  iot_api_client.apis.tags.properties_v2_api as PropertyV2
from dotenv import load_dotenv
import os, requests 
from oath_token_get import oauth_token_get
from datetime import datetime 

def coords_get(access_token, url):
    load_dotenv()
    THING_ID = os.getenv('THING_ID')
    
    # configure and instance the API client
    client_config = Configuration(host="https://api2.arduino.cc/iot")
    client_config.access_token = access_token
    client = iot.ApiClient(client_config)

    api_instance = PropertyV2.PropertiesV2List(client)

    # example passing only required values which don't have defaults set
    path_params = {
        'id': THING_ID,
    }
    query_params = {
    }
    header_params = {
    }

    try:
        # list properties_v2
        api_response = api_instance.properties_v2_list(
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
        )
    except ApiException as e:
        print("Exception when calling PropertiesV2Api->properties_v2_list: %s\n" % e)
    else:
        GPS = dict(dict(api_response.body[-1])['last_value'])
        now = datetime.now()
        data = {
            "lat": str(GPS['lat']),
            "lon": str(GPS['lon']),
            "time": str(now.strftime("%m/%d/%Y %H:%M:%S")),
        }
        requests.post(url, json=data)

if __name__ == "__main__":
    access_token = oauth_token_get()
    coords_get(access_token=access_token)