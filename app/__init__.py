from flask import Flask 
from flask_session import Session
from .commands import create_tables
from .extensions import db, mail
from .models import Posts, Comment, Replies, Author, Consultation, Payment, Admins, MyModelView

from .routes.main import main
from .routes.blog import blog
from .routes.purchase import purchase

from flask_admin import Admin

from flask_admin.contrib.sqla import ModelView

from .extensions import mail, login_manager




def create_app(config_file='settings.py'):
    app = Flask(__name__)
    
    app.config.from_pyfile(config_file)
    
    db.init_app(app)

    mail.init_app(app)

    login_manager.init_app(app)
    
    app.register_blueprint(main)
    app.register_blueprint(blog)
    app.register_blueprint(purchase)


    
    
    app.cli.add_command(create_tables)


    Session(app)

    


    admin = Admin(app)
    admin.add_view(MyModelView(Payment, db.session))
    admin.add_view(MyModelView(Posts, db.session))
    admin.add_view(MyModelView(Comment, db.session))
    admin.add_view(MyModelView(Replies, db.session))
    admin.add_view(MyModelView(Author, db.session))
    admin.add_view(MyModelView(Consultation, db.session))
    admin.add_view(MyModelView(Admins, db.session))


    
    return app