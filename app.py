from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
import json
from os import path, stat
import socket, atexit, time
from datetime import timedelta , datetime
import sqlite3, json


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
                thing_id = User.query.filter_by(email = email).first().tid
                session['thing_id'] = thing_id
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
    session.pop("thing_id", None)
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

        """if "lat" in json_data and "lon" in json_data and "time" in json_data and "thing_id" in json_data:
            markers.append({
                "lat": json_data["lat"],
                "lon": json_data["lon"],
                "time": json_data["time"],
                "thing_id": json_data["thing_id"]	
            })
            with open("data.json", "w") as file:
                json.dump(markers, file)
                
        else:
            return "Invalid data sent"
            """
        
    # This handles periodical requests from Front-end to display the saved coords
    elif request.method == "GET":
        connect = sqlite3.connect("instance/stalkinator.db")
        connect.row_factory = sqlite3.Row  # Set the row_factory to sqlite3.Row

        cur = connect.cursor()
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
        print(hahaha)
        return json.dumps(hahaha)

    else:
        return "Method not supported"

    return "OK\n"


if __name__ == "__main__":          
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=8080, debug=True)
