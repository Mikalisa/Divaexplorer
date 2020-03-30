from flask_wtf import FlaskForm
from wtforms import TextField, TextAreaField, SubmitField, validators

class ContactForm(FlaskForm):
  name = TextField("Name", [validators.Required("Please enter your name.")])
  email = TextField("Email", [validators.Required("Please enter your email address."), validators.Email()])
  subject = TextField("Subject",  [validators.Required("Please enter a subject.")])
  message = TextAreaField("Message", [validators.Required("Please enter a message.")])
  submit = SubmitField("Send")



class AdminLogin(FlaskForm):
  email = TextField("Email", [validators.Required("Please enter your email address."), validators.Email()])
  password = TextField("Password", [validators.Required("Please enter your password.")])
  submit = SubmitField("Log in")