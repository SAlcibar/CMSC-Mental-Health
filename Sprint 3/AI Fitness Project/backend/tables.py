from backend.db import db
from flask_login import UserMixin

# Creates our Sqlite table that holds user login/register info.
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    fitness_goals = db.Column(db.String(255), nullable=True)
    fitness_experience = db.Column(db.String(255), nullable=True)  # Comma-separated fitness experience levels
    workout_time = db.Column(db.String(255), nullable=True)  # Comma-separated preferred workout times
    dietary_preferences = db.Column(db.String(255), nullable=True)  # Comma-separated dietary preferences
    fitness_challenges = db.Column(db.String(255), nullable=True)  # Comma-separated fitness challenges

# Creates workout log table 
class WorkoutTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exercise = db.Column(db.String(100), nullable=False)
    sets = db.Column(db.Integer, nullable=False)
    reps = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# Creates cardio log table
class CardioTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    distance = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    minutes = db.Column(db.Integer, nullable=False)
    seconds = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    

    

    

