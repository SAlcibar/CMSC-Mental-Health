from flask import Flask, render_template, session
import os
from backend.db import db
from backend.tables import User
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask import Flask, render_template, redirect, url_for, flash
from flask_bcrypt import Bcrypt
from backend.forms import RegisterForm, LoginForm, SurveyForm, FitnessLogWorkoutForm, FitnessLogCardioForm
from backend.tables import User
import secrets


app = Flask(__name__)
bcrypt = Bcrypt(app)

# Handles our SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = secrets.token_hex(16)
db.init_app(app)

# Handles login verification
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Renders home page
@app.route('/', methods=['GET', 'POST'])
@login_required
def home():
    fitness_goals= current_user.fitness_goals

    if fitness_goals:
        fitness_goals_list = fitness_goals.split(",")
    else:
        fitness_goals_list = None
    return render_template('index.html', first_name=current_user.first_name, fitness_goals=fitness_goals_list)


# Renders fitness log page
@app.route('/fitness-log', methods=['GET', 'POST'])
def fitness_log():
    workout_form = FitnessLogWorkoutForm()
    cardio_form = FitnessLogCardioForm()
    return render_template('fitness-log.html', workout_form=workout_form, cardio_form=cardio_form)

# Renders about page
@app.route('/about')
def about():
    return render_template('about.html')

# Renders main AI chat page
@app.route('/main-chat')
def main_chat():
    return render_template('main-chat.html')

# Renders login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('home'))
    return render_template('login.html', form=form)

# Handles logout functionality
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Renders register page
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()


    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password, first_name=form.first_name.data, last_name=form.last_name.data)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('survey'))

    return render_template('register.html', form=form)

@app.route('/survey', methods=['GET', 'POST'])
def survey():
    form = SurveyForm()

    if form.validate_on_submit():
        selected_goals = ",".join(form.fitness_goals.data)
        current_user.fitness_goals = selected_goals
        db.session.commit()
        return redirect(url_for('home'))
    
    return render_template('survey.html', form=form)

with app.app_context():
    db.create_all()  

if __name__ == "__main__":

    app.run(debug=True, host="0.0.0.0", port=5000)
