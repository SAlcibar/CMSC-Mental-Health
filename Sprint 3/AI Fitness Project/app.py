from flask import Flask, render_template, session, request, redirect, url_for, flash, jsonify  # type: ignore # Add jsonify here
from flask_bcrypt import Bcrypt  # type: ignore
from flask_login import LoginManager, login_required, login_user, logout_user, current_user  # type: ignore
from flask_migrate import Migrate # type: ignore
from backend.db import db
from backend.tables import User, WorkoutTable, CardioTable
from backend.forms import RegisterForm, LoginForm, SurveyForm, FitnessLogWorkoutForm, FitnessLogCardioForm
import secrets
import openai  # type: ignore # Import the OpenAI library
import os

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
    # Retrieve fitness goals
    fitness_goals = current_user.fitness_goals
    fitness_goals_list = fitness_goals.split(",") if fitness_goals else None

    # Retrieve fitness experience
    fitness_experience = current_user.fitness_experience
    fitness_experience_list = fitness_experience.split(",") if fitness_experience else None

    # Retrieve workout time
    workout_time = current_user.workout_time
    workout_time_list = workout_time.split(",") if workout_time else None

    # Retrieve dietary preferences
    dietary_preferences = current_user.dietary_preferences
    dietary_preferences_list = dietary_preferences.split(",") if dietary_preferences else None

    # Retrieve fitness challenges
    fitness_challenges = current_user.fitness_challenges
    fitness_challenges_list = fitness_challenges.split(",") if fitness_challenges else None

    # Pass all data to the template
    return render_template(
        'index.html',
        first_name=current_user.first_name,
        fitness_goals=fitness_goals_list,
        fitness_experience=fitness_experience_list,
        workout_time=workout_time_list,
        dietary_preferences=dietary_preferences_list,
        fitness_challenges=fitness_challenges_list
    )

@app.route('/fitness-log', methods=['GET', 'POST'])
def fitness_log():
    workout_form = FitnessLogWorkoutForm()
    cardio_form = FitnessLogCardioForm()
    return render_template('fitness-log.html', workout_form=workout_form, cardio_form=cardio_form)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/main-chat', methods=['GET', 'POST'])
@login_required
def chat():
    user_id = current_user.id
    chat_context_file = os.path.join("chat_contexts", f"{user_id}_chat_context.txt")

    # Ensure the chat context directory exists
    if not os.path.exists("chat_contexts"):
        os.makedirs("chat_contexts")

    if request.method == 'GET':
        # Load recent chat context
        if os.path.exists(chat_context_file):
            with open(chat_context_file, 'r') as file:
                recent_context = file.read().strip()
        else:
            recent_context = ""

        # If the file is empty, set recent_context to an empty string
        if not recent_context:
            recent_context = ""

        # Render the main-chat.html page with recent context
        return render_template('main-chat.html', recent_context=recent_context)

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

        # Load recent chat context
        if os.path.exists(chat_context_file):
            with open(chat_context_file, 'r') as file:
                recent_context = file.read()
        else:
            recent_context = ""

        try:
            # Prepare the ChatGPT prompt with survey context and recent chat context
            messages = [
                {"role": "system", "content": "You are a helpful fitness assistant."},
                {"role": "system", "content": f"User's fitness goals: {', '.join(survey_context['fitness_goals'])}."},
                {"role": "system", "content": f"User's fitness experience: {', '.join(survey_context['fitness_experience'])}."},
                {"role": "system", "content": f"User's preferred workout time: {', '.join(survey_context['workout_time'])}."},
                {"role": "system", "content": f"User's dietary preferences: {', '.join(survey_context['dietary_preferences'])}."},
                {"role": "system", "content": f"User's fitness challenges: {', '.join(survey_context['fitness_challenges'])}."},
                {"role": "system", "content": f"Recent chat context: {recent_context}"},
                {"role": "user", "content": user_message}
            ]

            # Send the user's message to ChatGPT
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages
            )

            # Extract the response text
            chat_response = response['choices'][0]['message']['content']

            # Append the new conversation to the chat context
            with open(chat_context_file, 'a') as file:
                file.write(f"User: {user_message}\nAI: {chat_response}\n")

            return {"response": chat_response}, 200
        except Exception as e:
            return {"error": str(e)}, 500

@app.route('/exit-chat', methods=['POST'])
@login_required
def exit_chat():
    user_id = current_user.id
    chat_context_file = os.path.join("chat_contexts", f"{user_id}_chat_context.txt")

    # Load the full chat context
    if os.path.exists(chat_context_file):
        with open(chat_context_file, 'r') as file:
            full_context = file.read()
    else:
        full_context = ""

    # If the chat context is empty, skip summarization
    if not full_context.strip():
        return jsonify({'message': 'No chat context to summarize.'}), 200

    # Prompt ChatGPT to summarize the conversation
    summary_prompt = f"""
    Summarize the following conversation into 5 bullet points, focusing on important topics covered:
    {full_context}
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Updated model
            messages=[
                {"role": "system", "content": "You are a helpful assistant summarizing a conversation."},
                {"role": "user", "content": summary_prompt}
            ]
        )
        summary = response['choices'][0]['message']['content'].strip()

        # Combine the summary with the existing context
        updated_context = f"Summary:\n{summary}\n\nFull Conversation:\n{full_context}"

        # Write the updated context back to the file
        with open(chat_context_file, 'w') as file:
            file.write(updated_context)

        # Optionally clear the chat context after summarization
        with open(chat_context_file, 'w') as file:
            file.write("")  # Clear the file

        return jsonify({'message': 'Chat context updated and cleared successfully.'})
    except Exception as e:
        print(f"Error summarizing chat context: {e}")
        return jsonify({'message': 'Error summarizing chat context.'}), 500
    

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

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

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

@app.route('/survey', methods=['GET', 'POST'])
@login_required
def survey():
    form = SurveyForm()

    # Pre-fill the form with the user's existing answers
    if request.method == 'GET':
        if current_user.fitness_goals:
            form.fitness_goals.data = current_user.fitness_goals.split(",")
        if current_user.fitness_experience:
            form.fitness_experience.data = current_user.fitness_experience.split(",")
        if current_user.workout_time:
            form.workout_time.data = current_user.workout_time.split(",")
        if current_user.dietary_preferences:
            form.dietary_preferences.data = current_user.dietary_preferences.split(",")
        if current_user.fitness_challenges:
            form.fitness_challenges.data = current_user.fitness_challenges.split(",")

    # Save the form data when submitted
    if form.validate_on_submit():
        current_user.fitness_goals = ",".join(form.fitness_goals.data)
        current_user.fitness_experience = ",".join(form.fitness_experience.data)
        current_user.workout_time = ",".join(form.workout_time.data)
        current_user.dietary_preferences = ",".join(form.dietary_preferences.data)
        current_user.fitness_challenges = ",".join(form.fitness_challenges.data)

        # Commit changes to the database
        db.session.commit()

        flash("Survey updated successfully!", "success")
        return redirect(url_for('home'))

    return render_template('survey.html', form=form)

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