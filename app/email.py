from threading import Thread
from flask import current_app
from flask_mail import Message
from .extensions import mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, recipients, text_body):
    msg = Message(subject, recipients=recipients)
    msg.body = text_body
  
    Thread(target=send_async_email,
           args=(current_app._get_current_object(), msg)).start()