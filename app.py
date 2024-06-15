from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
import json
from os import path, stat
import socket, atexit, time
from datetime import timedelta , datetime


DATAFILE = "data.json"
markers = []
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stalkinator.db'
app.permanent_session_lifetime = timedelta(minutes= 5)
app.config['SECRET_KEY'] = 'averysecretkey'
db = SQLAlchemy(app)



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    tid = db.Column(db.String(100), nullable=True)
    
    def __init__(self, email,password, tid):
        self.email = email
        self.tid = tid
        self.password = password

@app.route("/" , methods = ["POST", "GET"])
@app.route("/login" , methods = ["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
    
        session.permanent = True
        session["email"] = email
        
        found_user = User.query.filter_by(email = email).first()

        if found_user:
            
            if password == found_user.password:
                return redirect(url_for('dashboard'))
            else:
                flash("Please type the correct PASSWORD !")
                session.pop("user",None)
                session.pop("pass", None)
                return render_template("login.html")
        
        else:
            flash("You've not register yet")
            session.pop("user",None)
            session.pop("pass", None)
            return render_template("login.html")
        
    
    else:
        if "user" in session:
            flash("Already Logged in")
            return redirect(url_for("home"))
        
        
        return render_template('login.html')
    
@app.route("/register" , methods = ["POST", "GET"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        thing_id = request.form["tid"]

        found_user = User.query.filter_by(email = email).first()
        if found_user:
            flash(" ACCOUNT EXISTED, PLEASE LOG IN!")
            session.pop("user",None)
            session.pop("pass", None)
            return redirect(url_for("login"))

        else:
            flash(f'Successfully registered for {email}! Please login.')
            account = User(email, password, thing_id)
            db.session.add(account)
            db.session.commit()
            return redirect(url_for("login"))
    else:
        return render_template("register.html")
    
@app.route('/logout')
def logout():
    session.pop("email", None)
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if "email" in session:
        return render_template("index.html", markers=markers)
    else:
        return redirect(url_for("login"))


@app.route("/data", methods=["POST", "GET"])
def data():
    # This handles requests from get_coords() to send new coords to be marked
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


if __name__ == "__main__":

    if not path.isfile(DATAFILE):
        # Create the file
        open(DATAFILE, "x")

    with open("data.json", "r") as file:
        if stat(DATAFILE).st_size != 0:
            markers = json.load(file)
            
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=8080, debug=True)
