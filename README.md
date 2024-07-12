# stalkinator

![Static Badge](https://img.shields.io/badge/Python-3.12.0-blue?style=flat&logo=Python&logoColor=white)

A Flask-based web application that tracks children's location to aid parental control using (mainly) Arduino Cloud.

## Setup

### Server-side

Clone this repo:

```bash
git clone git@github.com:emberfox205/stalkinator.git
```

Install all the dependencies (preferably into a virtual environment):

```bash
pip install -r requirements.txt
```

Register an [Arduio Cloud](https://cloud.arduino.cc/) account and subscribe to at least the **Maker** tier.

Register for a [Geoapify](https://www.geoapify.com/) key (free of charge).

In your local repo, set up an `.env` file with the following structure:

```bash
CLIENT_ID=arduino_client_id
CLIENT_SECRET=arduino_secret
GEOAPIFY_API_KEY="geoapify_api_key"
```

Replace `arduino_client_id`, `arduino_secret` and `geoapify_api_key` with actual data.

> [!NOTE]
> The Geoapify key must be quoted.

[Optionally] Install [DB Browser for SQLite](https://sqlitebrowser.org/dl/) to manage the database with a GUI.

### Client-side

Download mobile Arduino app for the tracked target:

- [iOS AppStore](https://apps.apple.com/vn/app/arduino-iot-cloud-remote/id1514358431?l=vi)
- [Android PlayStore](https://play.google.com/store/apps/details?id=cc.arduino.cloudiot&hl=en)

Turn the device into a Thing/Device and note the Thing ID to register on the web application.

> [!NOTE]
> When registering on the webpage, your email **matters** as emails informing whether the tracked target has left / entered safezone or entered dangerzone will be sent there. Check your spam in case you can not see them.

## Initialization

Run `app.py` for the application itself. Follow standard Flask procedures to open a localhost website. `app.py` can be run independently without Arduino data for demonstration purposes.

```bash
python app.py
```

Run `data_script.py` to interact with the Arduino Cloud API.

```bash
python data_script.py
```

> [!WARNING]
>
> - Only the Billiards category in the Dangerzone tab is functional. Other options are for demonstration.
> - Options in the Settings tab are for demonstration purposes only. They are, for now, out of scope of the project.

## Credits

- [GPS Tracking guide - Text](https://iot.microchip.com/docs/arduino/examples/GPS%20Tracker/Arduino%20Sketch)
- [GPS Tracking guide - Video](https://www.youtube.com/watch?v=WYT7r62AEYo&t=6s)
- [Icons](https://www.flaticon.com/)
- [Documentation for markers, circles and some other map elements](https://leafletjs.com/)
- [Map display](https://www.openstreetmap.org/)
