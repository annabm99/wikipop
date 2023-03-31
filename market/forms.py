# Page to make forms for users to fill (to register, for example)
from flask_wtf import FlaskForm # Specific flask package to make forms
from wtforms import StringField, PasswordField, SubmitField # Importing a certain type of field for the forms
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError # Validators for our form's requirements
from market.models import User


class RegisterForm(FlaskForm): # Inherits from the Flask form class
    
    # Function to alert if username already exists: username refers to the username column in the database
    def validate_username(self, username_to_check):
        # Check if username already exists
        user = User.query.filter_by(username=username_to_check.data).first()
        if user: # raise error if already exists
            raise ValidationError("Username already exists! Please log in or try a different username")
    # Same for email:
    def validate_email_address(self, email_address_to_check):
        email_address = User.query.filter_by(email_address=email_address_to_check.data).first()
        if email_address:
            raise ValidationError("Email Address already exists! Please try a different email address")

    # If more than one validator, they can be put in a list
    # Email validator checks for email sign, datarequired checks if in fact there is data in the field
    username = StringField(label="User Name:", validators=[Length(min=2, max=30), DataRequired()]) # The label is what will be displayed as header for the field
    email_address = StringField(label="Email Address:", validators = [Email(), DataRequired()])
    password1 = PasswordField(label="Password:", validators=[Length(min=6), DataRequired()]) # Different type of field for passwords
    password2 = PasswordField(label="Confirm Password:", validators=[EqualTo("password1"), DataRequired()]) # For password validation: it has to be equal to the 1st
    submit = SubmitField(label="Create Account")

class LoginForm(FlaskForm):
    username = StringField(label = "User Name:", validators=[DataRequired()])
    password = PasswordField(label = "Password:", validators=[DataRequired()])
    submit = SubmitField(label="Sign In")

class SearchForm(FlaskForm): # Inherits from the Flask form class
    word = StringField(label="", validators=[DataRequired()])
    submit = SubmitField(label="Sumbit")