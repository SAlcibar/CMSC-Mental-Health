from flask import Flask, render_template, session, request, redirect, url_for, flash, jsonify  # type: ignore # Add jsonify here
from flask_bcrypt import Bcrypt  # type: ignore
from flask_login import LoginManager, login_required, login_user, logout_user, current_user  # type: ignore
from flask_migrate import Migrate # type: ignore
from backend.db import db
from backend.tables import User, WorkoutTable, CardioTable
from backend.forms import RegisterForm, LoginForm, SurveyForm, FitnessLogWorkoutForm, FitnessLogCardioForm
import secrets
import openai  # type: ignore # Import the OpenAI library


# Set your OpenAI API key

# Initialize Flask app
app = Flask(__name__)
bcrypt = Bcrypt(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Configure the app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = secrets.token_hex(16)
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))  # Use Session.get() instead of Query.get()
login_manager.login_message = None


# Define routes
@app.route('/', methods=['GET', 'POST'])
@login_required
def home():
    fitness_goals = current_user.fitness_goals
    fitness_goals_list = fitness_goals.split(",") if fitness_goals else None
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

@app.route('/main-chat', methods=['GET', 'POST'])
@login_required
def chat():
    if request.method == 'GET':
        # Render the main-chat.html page for GET requests
        return render_template('main-chat.html')

    if request.method == 'POST':
        # Retrieve the user's survey responses
        survey_context = {
            "fitness_goals": current_user.fitness_goals.split(",") if current_user.fitness_goals else [],
            "fitness_experience": current_user.fitness_experience.split(",") if current_user.fitness_experience else [],
            "workout_time": current_user.workout_time.split(",") if current_user.workout_time else [],
            "dietary_preferences": current_user.dietary_preferences.split(",") if current_user.dietary_preferences else [],
            "fitness_challenges": current_user.fitness_challenges.split(",") if current_user.fitness_challenges else []
        }

        # Get the user's message from the request
        user_message = request.json.get('message')
        if not user_message:
            return {"error": "No message provided"}, 400

        try:
            # Prepare the ChatGPT prompt with survey context
            messages = [
                {"role": "system", "content": "You are a helpful fitness assistant."},
                {"role": "system", "content": f"User's fitness goals: {', '.join(survey_context['fitness_goals'])}."},
                {"role": "system", "content": f"User's fitness experience: {', '.join(survey_context['fitness_experience'])}."},
                {"role": "system", "content": f"User's preferred workout time: {', '.join(survey_context['workout_time'])}."},
                {"role": "system", "content": f"User's dietary preferences: {', '.join(survey_context['dietary_preferences'])}."},
                {"role": "system", "content": f"User's fitness challenges: {', '.join(survey_context['fitness_challenges'])}."},
                {"role": "user", "content": user_message}
            ]

            # Send the user's message to ChatGPT
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages
            )

            # Extract the response text
            chat_response = response['choices'][0]['message']['content']
            return {"response": chat_response}, 200
        except Exception as e:
            return {"error": str(e)}, 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash("Login successful!")
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
        flash("Registration Successful!")
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password, first_name=form.first_name.data, last_name=form.last_name.data)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('survey'))

    return render_template('register.html', form=form)


# Renders survey page
@app.route('/survey', methods=['GET', 'POST'])
def survey():
    form = SurveyForm()

    if form.validate_on_submit():
        selected_goals = ",".join(form.fitness_goals.data)
        current_user.fitness_goals = selected_goals
        db.session.commit()
        return redirect(url_for('home'))
    
    return render_template('survey.html', form=form)


# Renders workout log page
@app.route('/workout-log', methods=['GET', 'POST'])
@login_required
def workout_log():
    form = FitnessLogWorkoutForm()

    if form.validate_on_submit():
        flash("Workout Log Submitted!")
        exercises = request.form.getlist('exercise_input')
        sets = request.form.getlist('sets_field')
        reps = request.form.getlist('reps_field')
        for i in range(len(exercises)):
            if exercises[i] and sets[i].isdigit() and reps[i].isdigit():
                workout = WorkoutTable(
                    exercise=exercises[i],
                    sets=int(sets[i]),
                    reps=int(reps[i]),
                    user_id=current_user.id)
                db.session.add(workout)

        db.session.commit()
        return redirect('/fitness-log')
    return render_template('workout-log.html', form=form)


# Renders cardio log page
@app.route('/cardio-log', methods=['GET', 'POST'])
@login_required
def cardio_log():
    form = FitnessLogCardioForm()

    if request.method == 'POST' and form.validate_on_submit():
        flash("Cardio Log Submitted!")
        distances = request.form.getlist('distance_field')
        minutes = request.form.getlist('minute_field')
        seconds = request.form.getlist('second_field')

        for i in range(len(distances)):
            if distances[i] and minutes[i].isdigit() and seconds[i].isdigit():
                cardio = CardioTable(
                    distance=distances[i],
                    minutes=int(minutes[i]),
                    seconds=int(seconds[i]),
                    user_id=current_user.id
                )
                db.session.add(cardio)

        db.session.commit()
        return redirect('/fitness-log')

    return render_template('cardio-log.html', form=form)


# Initialize the database
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
