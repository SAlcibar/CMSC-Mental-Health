from flask_wtf import FlaskForm  # type: ignore
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    SelectMultipleField,
    widgets,
    IntegerField,
    RadioField,
    DecimalField,
)  # type: ignore
from wtforms.validators import InputRequired, Length, ValidationError, DataRequired, NumberRange  # type: ignore
from backend.tables import User
from flask import flash  # type: ignore


# Sets up the form on the register page
class RegisterForm(FlaskForm):
    username = StringField(
        validators=[InputRequired(), Length(min=4, max=20)],
        render_kw={"placeholder": "Username"},
    )
    password = PasswordField(
        validators=[InputRequired(), Length(min=4, max=20)],
        render_kw={"placeholder": "Password"},
    )
    first_name = StringField(
        validators=[InputRequired(), Length(min=1)],
        render_kw={"placeholder": "First Name"},
    )
    last_name = StringField(
        validators=[InputRequired(), Length(min=1)],
        render_kw={"placeholder": "Last Name"},
    )

    submit = SubmitField("Register")

    def validate_username(self, username):
        existing_user = User.query.filter_by(username=username.data).first()
        if existing_user:
            flash("Username already exists!")
            raise ValidationError("That username already exists.")


# Sets up form on login page
class LoginForm(FlaskForm):
    username = StringField(
        validators=[InputRequired(), Length(min=4, max=20)],
        render_kw={"placeholder": "Username"},
    )

    password = PasswordField(
        validators=[InputRequired(), Length(min=4, max=20)],
        render_kw={"placeholder": "Password"},
    )

    submit = SubmitField("Login")


# Sets up form on survey page
class SurveyForm(FlaskForm):
    # First question: Multiple selection (checkboxes)
    fitness_goals = SelectMultipleField(
        "What are your fitness goals?",
        choices=[
            ("Build Muscle", "Build Muscle"),
            ("Lose Weight", "Lose Weight"),
            ("Increase Strength", "Increase Strength"),
            ("Improve Cardio", "Improve Cardio"),
        ],
        option_widget=widgets.CheckboxInput(),
        widget=widgets.ListWidget(prefix_label=False),
    )

    # Second question: Single selection (radio buttons)
    fitness_experience = RadioField(
        "What is your fitness experience level?",
        choices=[
            ("Beginner", "Beginner"),
            ("Intermediate", "Intermediate"),
            ("Advanced", "Advanced"),
        ],
        widget=widgets.ListWidget(prefix_label=False),
        validators=[DataRequired()],
    )

    # Third question: Multiple selection (checkboxes)
    workout_time = SelectMultipleField(
        "What time of day do you prefer to work out?",
        choices=[
            ("Morning", "Morning"),
            ("Afternoon", "Afternoon"),
            ("Evening", "Evening"),
            ("No Preference", "No Preference"),
        ],
        option_widget=widgets.CheckboxInput(),
        widget=widgets.ListWidget(prefix_label=False),
    )

    # Fourth question: Single selection (radio buttons)
    dietary_preferences = RadioField(
        "Do you have any dietary preferences or restrictions?",
        choices=[
            ("Vegetarian", "Vegetarian"),
            ("Vegan", "Vegan"),
            ("Gluten-Free", "Gluten-Free"),
            ("No Restrictions", "No Restrictions"),
        ],
        widget=widgets.ListWidget(prefix_label=False),
        validators=[DataRequired()],
    )

    # Fifth question: Multiple selection (checkboxes)
    fitness_challenges = SelectMultipleField(
        "What are your biggest fitness challenges?",
        choices=[
            ("Time Management", "Time Management"),
            ("Motivation", "Motivation"),
            ("Injury Recovery", "Injury Recovery"),
            ("Access to Equipment", "Access to Equipment"),
        ],
        option_widget=widgets.CheckboxInput(),
        widget=widgets.ListWidget(prefix_label=False),
    )

    submit = SubmitField("Submit")


# Sets up form on workout log page
class FitnessLogWorkoutForm(FlaskForm):
    reps_field = IntegerField(
        "Total Reps",
        default=1,
        validators=[NumberRange(min=0, message="Value must be 0 or greater")],
    )

    sets_field = IntegerField(
        "Total Sets",
        default=1,
        validators=[NumberRange(min=0, message="Value must be 0 or greater")],
    )

    exercise_input = StringField(
        validators=[InputRequired(), Length(min=1, max=50)],
        render_kw={"placeholder": "Exercise Input"},
    )

    submit = SubmitField("Submit")


# Sets up form on cardio log page
class FitnessLogCardioForm(FlaskForm):
    minute_field = IntegerField(
        "Minutes", default=0, validators=[NumberRange(min=0)]
    )

    second_field = IntegerField(
        "Seconds", default=0, validators=[NumberRange(min=0, max=59)]
    )

    distance_field = DecimalField(
        "Total Miles",
        default=0,
        validators=[InputRequired(), NumberRange(min=0, message="Value must be 0 or greater")],
    )

    submit = SubmitField("Submit")