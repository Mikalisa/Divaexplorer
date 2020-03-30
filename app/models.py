from .extensions import db
from datetime import datetime, timedelta
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, UserMixin

## classes for the database

class Posts(db.Model):
    __searchable__  = ['title', 'content']
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    content = db.Column(db.String(8000))
    youtube_link = db.Column(db.String(30))
    image_path = db.Column(db.String(100))
    posted_time = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    comments = db.relationship('Comment', backref='posts', cascade="all, delete-orphan", lazy='dynamic', primaryjoin="Posts.id == Comment.parent_id")
    
    def __repr__(self):
        return '<Post {}>'.format(self.content)



#wa.whoosh_index(app, Posts)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(800))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)


    replies = db.relationship('Replies', backref='comment', cascade="all, delete-orphan", lazy='dynamic', primaryjoin="Comment.id == Replies.parent_id")


    author_id = db.Column(db.Integer, db.ForeignKey('author.id'))
   
    def __repr__(self):
        return f"Comment('{self.content}', '{self.timestamp}')"
    


class Replies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(800))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=False)
    

    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)

    def __repr__(self):
        return f"Reply('{self.content}', '{self.timestamp}')"


class Author(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(100))
    user_name = db.Column(db.String(32))
    user_email = db.Column(db.String(32))
    user_photo = db.Column(db.String(200))

    
    # relationship with comments for linking authors
    comments = db.relationship('Comment', backref='author', lazy='dynamic')

    replies = db.relationship('Replies', backref='author', lazy='dynamic')

    payment = db.relationship('Payment', backref='author', lazy='dynamic')

    
    def __repr__(self):
        return f"Author('{self.user_name}', '{self.user_email}')"
    
    def is_active(self):
        return True

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3

    def is_authenticated(self):
        return True



class Consultation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer)
    title = db.Column(db.String(32), nullable=False)
    desc = db.Column(db.String())
    

    def __repr__(self):
        return f"Consultation('{self.price}', '{self.title}')"



class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    payer_email = db.Column(db.String(100))
    unix = db.Column(db.String(100))
    payment_date = db.Column(db.String(100))
    username = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    payment_gross = db.Column(db.Float(6,2))
    payment_fee = db.Column(db.Float(6,2))
    payment_net = db.Column(db.Float(6,2))
    payment_status = db.Column(db.String(30))
    txn_id = db.Column(db.String(100))
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)

    def __repr__(self):
        return f"Payment('{self.price}', '{self.title}')"



class Admins(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(100))

    def is_active(self):
        return True

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3

    def __repr__(self):
        return f"Admins('{self.username}', '{self.last_name}')"



class MyModelView(ModelView):
    def is_accessible(self):
        return True
    