# Successful
import iot_api_client as iot
from iot_api_client.rest import ApiException
from iot_api_client.configuration import Configuration
import  iot_api_client.apis.tags.properties_v2_api as PropertyV2
from dotenv import load_dotenv
import os, requests 
from libs.oauth_token_get import oauth_token_get
from datetime import datetime 
import sqlite3


def coords_get(access_token, thing_id, cur, connect):
    
    # configure and instance the API client
    client_config = Configuration(host="https://api2.arduino.cc/iot")
    client_config.access_token = access_token
    client = iot.ApiClient(client_config)

    api_instance = PropertyV2.PropertiesV2List(client)

    # example passing only required values which don't have defaults set
    path_params = {
        'id': thing_id,
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
        
        values = [float(GPS['lat']),float(GPS['lon']),str(now.strftime("%d/%m/%Y %H:%M:%S")),str(thing_id)]

        cur.execute("""CREATE TABLE IF NOT EXISTS Makers (ID INTEGER PRIMARY KEY AUTOINCREMENT, lat real, lon real, time string, thing_id) """)
        connect.commit()
        
        cur.execute("INSERT INTO Makers (lat, lon, time, thing_id) VALUES (?,?,?,?)",values)
        connect.commit()

        
    	
if __name__ == "__main__":
    access_token = oauth_token_get()
    coords_get(access_token=access_token)