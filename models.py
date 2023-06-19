from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from sqlalchemy.orm import backref


db = SQLAlchemy()

def connect_db(app):
    db.app = app
    db.init_app(app)

class User(db.Model):
    __tablename__ = 'users'

    username = db.Column(db.String(20),
                        primary_key=True)
    
    password = db.Column(db.Text,
                        nullable=False)

    email = db.Column(db.String(50),
                    nullable=False,
                    unique=True) 

    first_name = db.Column(db.String(30),
                    nullable=False)

    last_name = db.Column(db.String(30),
                    nullable=False)


class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer,
                    primary_key=True,
                    autoincrement=True)

    title = db.Column(db.String(100),
                    nullable=False)

    content = db.Column(db.Text,
                    nullable=False)
    
    username = db.Column(db.String(20),
                            db.ForeignKey('users.username'))

    user = db.relationship('User', backref = backref('reviews', cascade='all,delete-orphan'))
    