from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField
from wtforms.validators import InputRequired, ValidationError


def length_validator(val):
    def validation(form, field):
        value = len(field.data)
        if value > val or val < 1:
            raise ValidationError("f'Field must have a length of {val} characters.'")

    return validation


class RegisterForm(FlaskForm):
    username = StringField(
        "Username", validators=[InputRequired(), length_validator(20)]
    )
    password = PasswordField("Password", validators=[InputRequired()])
    password_check = PasswordField("Verify Password", validators=[InputRequired()])
    email = EmailField("Email", validators=[InputRequired(), length_validator(50)])
    first_name = StringField(
        "First name", validators=[InputRequired(), length_validator(30)]
    )
    last_name = StringField(
        "Last name", validators=[InputRequired(), length_validator(30)]
    )


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])


class FeedbackForm(FlaskForm):
    title = StringField("Title", validators=[InputRequired(), length_validator(100)])
    content = StringField("Content", validators=[InputRequired()])
