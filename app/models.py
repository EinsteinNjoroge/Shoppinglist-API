from flask_bcrypt import Bcrypt
from app import db


class User(db.Model):
    """This class defines the users table """
    __tablename__ = 'users'
    id = db.Column('id', db.Integer, primary_key=True)
    username = db.Column('username', db.String(50), unique=True)
    firstname = db.Column('firstname', db.String(10), nullable=False)
    lastname = db.Column('lastname', db.String(10), nullable=False)
    password = db.Column('password', db.String(100), nullable=False)

    def __init__(self, username, password, firstname, lastname):
        """Initialize the user """
        self.username = username
        self.firstname = firstname
        self.lastname = lastname
        self.password = Bcrypt().generate_password_hash(password).decode()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Shoppinglists(db.Model):
    """This class defines the shoppinglists table """
    __tablename__ = 'shoppinglists'
    id = db.Column('id', db.Integer, primary_key=True)
    title = db.Column('title', db.String(10), nullable=False)

    # create virtual column for maintaining table relationship and data integrity
    shoppinglists_items = db.relationship(
        "ShoppingListItems", backref="shoppinglists", lazy="dynamic")


class ShoppingListItems(db.Model):
    """This class defines the shopping-lists items table """
    __tablename__ = 'shoppinglist_items'
    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column('name', db.String(10), nullable=False)
    shoppinglist_id = db.Column(
        db.Integer, db.ForeignKey(
            'shoppinglists.shoppinglist_id',
            onupdate="CASCADE",
            ondelete="CASCADE"
        ),
        nullable=False
    )
