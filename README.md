# stalkinator

![Static Badge](https://img.shields.io/badge/Python-3.12.0-blue?style=flat&logo=Python&logoColor=white)

A Flask-based webapp to monitor positions using Arduino 

# Setup

## Server-side

Clone this repo: 

`git clone git@github.com:emberfox205/stalkinator.git` 

Install all the dependencies:

`pip install -r requirements.txt`

Register an [Arduio Cloud](https://cloud.arduino.cc/) account and subscribe to at least the **Maker** tier. 

Register for a Geoapify API key: https://www.geoapify.com/

In your local repo, set up an `.env` file with the following structure:

```
CLIENT_ID=arduino_client_id
CLIENT_SECRET=arduino-Secret
GEOAPIFY_API_KEY=geoapify_api_key
```
Replace `arduino_client_id`, `arduino_secret` and `geoapify_api_key` with actual data. 

## Client-side 

Download mobile Arduino app for the tracked target: 

- [iOS AppStore](https://apps.apple.com/vn/app/arduino-iot-cloud-remote/id1514358431?l=vi)
- [Android PlayStore](https://play.google.com/store/apps/details?id=cc.arduino.cloudiot&hl=en)

Turn the device into a Thing/Device and note the Thing ID to register on the web application.

> [!NOTE] 
> When registering on the webpage, your email **matters** as emails informing whether the tracked target has left / entered safezone or entered dangerzone will be sent there. Check your spam in case you can not see them.

# Initialization

Run two files: `app.py` for the server itself, and `data_script.py` for interaction with Arduino Cloud API.

> [!WARNING]
> A bug persists in the Dangerzone section which prevents Dangerzone markers to be displayed on the map. Reload a few times for them to appear. Probably will not be fixed.

# Credits: 

 - [GPS Tracking guide - text](https://iot.microchip.com/docs/arduino/examples/GPS%20Tracker/Arduino%20Sketch)
 - [GPS Tracking guide - vid](https://www.youtube.com/watch?v=WYT7r62AEYo&t=6s)
 - [Icons](https://www.flaticon.com/)
 - [Markers, Safezone and other map interactions](https://leafletjs.com/)
 - [Map display](https://www.openstreetmap.org/)
