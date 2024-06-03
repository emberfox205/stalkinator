from flask import Flask, render_template, request
from apscheduler.schedulers.background import BackgroundScheduler
import json
from os import path, stat
from oath_token_get import oauth_token_get
from coords_get import coords_get
import socket, time, atexit, datetime

DATAFILE = "data.json"

markers = []

app = Flask(__name__)

# Global var, bad idea
latest_token = None


@app.route("/data", methods=["POST", "GET"])
def data():
    # This handles requests to send new coords to be marked
    if request.method == "POST":
        json_data = {}

        try:
            json_data = json.loads(request.data.decode("utf8"))
        except:
            return "Error decoding JSON"

        if "lat" in json_data and "lon" in json_data and "time" in json_data:
            markers.append({
                "lat": json_data["lat"],
                "lon": json_data["lon"],
                "time": json_data["time"],
                "index": len(markers)
            })

            with open("data.json", "w") as file:
                json.dump(markers, file)
        else:
            return "Invalid data sent"
    # This handles periodical requests from Front-end to display the saved coords
    elif request.method == "GET":

        if "index" in request.args:
            index = int(
                request.args["index"]) if request.args["index"]. isdigit() else None

            if index < 0 or index == None:
                return "Invalid index"
            elif index >= len(markers):
                return "No new entries"
            else:
                # Send a list of new markers to the Front-end
                return json.dumps(markers[index:])
        else:
            return "No index present"

    else:
        return "Method not supported"

    return "OK\n"


@app.route("/")
def root():
    return render_template("index.html", markers=markers)

# A wrapper to get the value returned by oauth
def update_token():
    global latest_token
    latest_token = oauth_token_get()

def get_coords():
    while not latest_token:
        time.sleep(1)
    ipv4_address = socket.gethostbyname(socket.gethostname())
    coords_get(access_token=latest_token, url=f"http://{ipv4_address}:8080/data")

# 
scheduler = BackgroundScheduler(job_defaults={'max_instances': 1})
scheduler.add_job(func=update_token, trigger="interval", seconds=250, next_run_time=datetime.datetime.now())
scheduler.add_job(func=get_coords, trigger="interval", seconds=10, next_run_time=datetime.datetime.now())

if __name__ == "__main__":

    if not path.isfile(DATAFILE):
        # Create the file
        open(DATAFILE, "x")

    with open("data.json", "r") as file:
        if stat(DATAFILE).st_size != 0:
            markers = json.load(file)
            
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())
    app.run(host="0.0.0.0", port=8080, debug=True)
