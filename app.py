from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import json
from os import path, stat
import socket, atexit, time
from datetime import timedelta , datetime
import sqlite3, json
import subprocess
from libs.get_places import get_user_coords, fetch_places, save_places_to_db, haversine


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

def distance_safe(connect, cur, marker):
    cur.execute("SELECT lat, lon, safeRange FROM safeZone WHERE email = ? order by ID DESC Limit 1", (session['email'],))
    safeZones = cur.fetchall() 
    if not safeZones:   
        print(f"{session["email"]} does not have a safe zone set up.")
        return None
    for safeZone in safeZones:
        safeZone = dict(safeZone)
        distance = haversine(marker['lat'], marker['lon'], safeZone['lat'], safeZone['lon'])
        print(distance, safeZone['safeRange'])
        if distance < safeZone['safeRange']:
            print(f"{session["email"]} is in the safe zone")
        else:
            print(f"{session["email"]} is not in the safe zone")        
    return distance

def distance_danger(connect, cur, marker):
    
    cur.execute("SELECT name, lat, lon, distance FROM geofence WHERE thing_id = ?", (session['thing_id'],))
    dangerZones = cur.fetchall()
    #print("DANGER", [dict(i) for i in dangerZones]) 
    if not dangerZones:   
        print(f"{session["email"]} does not have dangerZone yet reload.")
        return None
    dangers = [] 
    for dangerZone in dangerZones:
        dangerZone = dict(dangerZone)
        distance = dangerZone['distance']
        if distance < 100:
            dangers.append(dangerZone, distance)
    if dangers:
        print(f"{session["email"]} is in the danger zone")
    else: 
        print(f"{session["email"]} is not in the danger zone")
                   
    return dangers

def getdb(thing_id):
    conn = sqlite3.connect("instance/stalkinator.db")
    cur = conn.cursor()  
    cur.execute('''CREATE TABLE IF NOT EXISTS geofence 
                (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, lat REAL, lon REAL, thing_id TEXT, distance REAL)''')  
    cur.execute("SELECT name, lat, lon, distance FROM geofence WHERE thing_id = ?", (thing_id,))
    geofences = cur.fetchall()
    
    lat, lon = get_user_coords(thing_id=thing_id)
    if lat is not None and lon is not None:
        places = fetch_places(lat, lon)
        save_places_to_db(places, thing_id, lat, lon)
    conn.close()
    return geofences

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
                thing_id = User.query.filter_by(email = email).first().tid
                session['thing_id'] = thing_id
                
                return redirect(url_for('dashboard'))
            else:
                flash("Please type the correct PASSWORD !")
                session.pop("email",None)
                session.pop("pass", None)
                return render_template("login.html")
        
        else:
            flash("You've not register yet")
            session.pop("email",None)
            session.pop("pass", None)
            return render_template("login.html")
        
    
    else:
        if "email" in session:
            flash("Already Logged in")
            return redirect(url_for("dashboard"))
        
        
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
            session.pop("email",None)
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
    session.pop("thing_id", None)
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if "email" in session:
        thing_id = session.get('thing_id')
        geofences = getdb(thing_id)
        return render_template("index.html", geofences=geofences)
    else:
        return redirect(url_for("login"))


@app.route("/data", methods=["POST", "GET"])
def data():
    connect = sqlite3.connect("instance/stalkinator.db")
    connect.row_factory = sqlite3.Row  # Set the row_factory to sqlite3.Row
    cur = connect.cursor()
    
    # This handles requests from get_coords() to send new coords to be marked
    if request.method == "POST" and all(isinstance(float(request.form.get(key)), float) for key in ["lat", "lon", "safeRange"]):
        
        try:
            lat = request.form.get("lat")	
            lon = request.form.get("lon")
            safeRange = request.form.get("safeRange")
            values = [lat, lon, safeRange, session['email']]
            print(f"{session["email"]}",safeRange)
            cur.execute("""CREATE TABLE IF NOT EXISTS safeZone (ID INTEGER PRIMARY KEY AUTOINCREMENT, lat real, lon real, safeRange integer, email text) """)
            cur.execute("INSERT INTO safeZone (lat, lon, safeRange, email) VALUES (?, ?, ?, ?)", values)
            connect.commit()
        except:
            return "Error decoding JSON"
        
    # This handles periodical requests from Front-end to display the saved coords
    elif request.method == "GET":
       
        # Execute a query
        cur.execute("""CREATE TABLE IF NOT EXISTS Makers (ID INTEGER PRIMARY KEY AUTOINCREMENT, lat real, lon real, time string, thing_id) """)
        cur.execute(f"SELECT lon, lat, time FROM Makers WHERE thing_id = '{session['thing_id']}' order by time desc LIMIT 20")
        # Fetch all rows as dictionaries
        rows = cur.fetchall()
        markers = []
        for i, row in enumerate(rows):
            row = dict(row)
            row["index"] = i
            markers.append(row)
        
        hahaha = sorted(markers, key=lambda x: x['index'], reverse=True)
        distance_safe(connect, cur, markers[-1])
        print(distance_danger(connect, cur, markers[-1]))
        return json.dumps(hahaha)

    else:
        return "Method not supported"

    return "OK\n"

if __name__ == "__main__":          
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=8080, debug=True)
