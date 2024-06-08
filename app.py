from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_required, logout_user, current_user, LoginManager, login_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import  InputRequired, Length, Email, ValidationError   

from apscheduler.schedulers.background import BackgroundScheduler
import json
from os import path, stat
from oath_token_get import oauth_token_get
from coords_get import coords_get
import socket, atexit, time
from datetime import timedelta , datetime
DATAFILE = "data.json"

markers = []

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stalkinator.db'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=50)
app.config['SECRET_KEY'] = 'averysecretkey'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = 'login'
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    tid = db.Column(db.String(100), nullable=False)
    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"
    
class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(), Length(min=10, max=80)],
                        render_kw={"placeholder": "Enter your Email"})
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6, max=50)],
                             render_kw={"placeholder": "Enter your Password"})
    tid =  StringField('Thing ID', validators=[InputRequired(), Length(min=6, max=50)],
                             render_kw={"placeholder": "Enter your Thing's Thing ID"})
    submit = SubmitField('Register')
    def validate_email(self, email):
        exist_email = User.query.filter_by(email=email.data).first()
        if exist_email:
            raise ValidationError('That email is taken. Please choose a different one.')
    
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Length(min=10, max=80)],
                        render_kw={"placeholder": "Enter your Email"})
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6, max=50)],
                             render_kw={"placeholder": "Enter your Password"})
    
    submit = SubmitField('Login')
    
@app.route('/')
def prelogin():
    return redirect(url_for('login'))
@app.route('/login',  methods = ["POST", "GET"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if user.password == form.password.data:
                login_user(user)
                session.permanent = True
                return redirect(url_for('dashboard'))
    return render_template('login.html', form=form)

@app.route("/register",  methods = ["POST", "GET"])
def register():
    form = RegisterForm()
    
    if form.validate_on_submit():
        user = User(email=form.email.data, password=form.password.data, tid=form.tid.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Successfully registered for {form.email.data}! Please login.')
        return redirect(url_for('login'))
    return render_template("register.html", form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template("index.html", markers=markers)


# Global var, bad idea
latest_token = None
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
 

# A wrapper to get the value returned by oauth
def update_token():
    global latest_token
    latest_token = oauth_token_get()

# Send POST requests to update data.json
def get_coords():
    while not latest_token:
        time.sleep(1)
    ipv4_address = socket.gethostbyname(socket.gethostname())
    # Flexibily set the IP address (for dev env only that is)
    coords_get(access_token=latest_token, url=f"http://{ipv4_address}:8080/data")

# Initiate scheduler (To run multiprocessing)
scheduler = BackgroundScheduler(job_defaults={'max_instances': 1})
scheduler.add_job(func=update_token, trigger="interval", seconds=250, next_run_time=datetime.now())
scheduler.add_job(func=get_coords, trigger="interval", seconds=10, next_run_time=datetime.now())

if __name__ == "__main__":

    if not path.isfile(DATAFILE):
        # Create the file
        open(DATAFILE, "x")

    with open("data.json", "r") as file:
        if stat(DATAFILE).st_size != 0:
            markers = json.load(file)
            
    scheduler.start()
    # Exit the scheduler as the server shuts down
    atexit.register(lambda: scheduler.shutdown())
    app.run(host="0.0.0.0", port=8080, debug=True)
