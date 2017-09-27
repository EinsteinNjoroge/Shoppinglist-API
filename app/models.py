import os
import random
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import BadSignature
from itsdangerous import SignatureExpired


db = SQLAlchemy()  # initialize sql-alchemy
secret_key = os.urandom(24)  # create a random secret key


def generate_random_id():
    """generates a random integer value between 1 and 100000000
        :return
            (int): randomly generated integer
    """
    random_id = random.randrange(1, 100000000)
    return random_id


class User(db.Model):
    """This class defines the users table """
    __tablename__ = 'users'
    id = db.Column('id', db.Integer, primary_key=True)
    username = db.Column('username', db.String(50), unique=True)
    firstname = db.Column('firstname', db.String(10), nullable=False)
    lastname = db.Column('lastname', db.String(10), nullable=False)
    password_hash = db.Column('password_hash', db.String(100), nullable=False)

    # create virtual column (back-reference)
    # for maintaining table relationship and data integrity
    users = db.relationship(
        "Shoppinglists", backref="users", lazy="dynamic")

    def __init__(self, username, password_hash, firstname='', lastname=''):
        """Initialize the user """
        self.id = generate_random_id()
        self.username = username
        self.firstname = firstname
        self.lastname = lastname
        self.password_hash = password_hash

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(secret_key)

        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token

        user = User.query.get(data['id'])
        return user


class Shoppinglists(db.Model):
    """This class defines the shoppinglists table """
    __tablename__ = 'shoppinglists'
    id = db.Column('id', db.Integer, primary_key=True)
    title = db.Column('title', db.String(100), nullable=False)
    user_id = db.Column(
        'user_id', db.Integer,
        db.ForeignKey(
            'users.id',
            onupdate="CASCADE",
            ondelete="CASCADE"
        ),
        nullable=False)

    # create virtual column (back-reference)
    # for maintaining table relationship and data integrity
    shoppinglists_items = db.relationship(
        "ShoppingListItems", backref="shoppinglists", lazy="dynamic")

    def __init__(self, title):
        """Initialize with a title"""
        self.title = title
        self.id = generate_random_id()
        self.user_id = 1  # session["current_user"]

    @staticmethod
    def get_all():
        return Shoppinglists.query.all()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class ShoppingListItems(db.Model):
    """This class defines the shopping-lists items table """
    __tablename__ = 'shoppinglist_items'
    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column('name', db.String(100), nullable=False)
    shoppinglist_id = db.Column(
        db.Integer, db.ForeignKey(
            'shoppinglists.id',
            onupdate="CASCADE",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    def __init__(self, name, shoppinglist_id):
        """Initialize with a title"""
        self.name = name
        self.id = generate_random_id()
        self.shoppinglist_id = shoppinglist_id

    @staticmethod
    def get_all():
        return ShoppingListItems.query.all()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
