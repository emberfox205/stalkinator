from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_required, logout_user, current_user, LoginManager, login_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import  InputRequired, Length, Email, ValidationError   


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stalkinator.db'
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
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True) 