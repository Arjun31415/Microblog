import datetime
import uuid

import flask_login
from flask import session

from blog import Blog
from database.db import Database

bcrypt = None


class User(flask_login.UserMixin):

    """
    User class for login, register and fetching user.
    Uses sessions for login
    """

    def __init__(self, email, password=None, _id=None):
        # super().__init__()
        self.email = email
        # Ensure the password is hashed before calling init
        self.auth = None
        self.password = password
        self._id = uuid.uuid4().hex if _id is None else _id

    @classmethod
    def get_by_email(cls, email):
        data = Database.find_one("users", {'email': email})
        if data is not None:
            return cls(**data)
        return None

    @classmethod
    def get_by_id(cls, _id):
        data = Database.find_one("users", {'_id': _id})
        if data is not None:
            return cls(**data)
        return None

    @staticmethod
    def login_valid(email, password):
        # User.login_valid("arjunp@amazing.com",1234)
        # Check whether a user's email matches the password they sent us
        user = User.get_by_email(email)
        if user is not None:
            # check password
            print(bcrypt.generate_password_hash(
                "1234".encode('utf8')).decode("utf-8"))
            return bcrypt.check_password_hash(user.password, password)
        return False

    @classmethod
    def register(cls, email, password):
        user = User.get_by_email(email)
        print("user: ", user)
        if user is None:
            # User does not exist so create a new user
            hashed_pwd = bcrypt.generate_password_hash(
                password.encode('utf8')).decode("utf-8")
            cls(email, hashed_pwd).save_to_db()
            session['email'] = email
            return True
        else:
            # User exists
            return False

    @staticmethod
    def login(user_email):
        # ensure Login_valid has already been called
        session['email'] = user_email

    @staticmethod
    def logout():
        # User has been logged out
        session['email'] = None

    def get_blogs(self):
        return Blog.find_by_author_id(self._id)

    def new_blog(self, title, description):
        blog = Blog(
            author=self.email,
            title=title,
            description=description,
            author_id=self._id
        )
        blog.save_to_mongo()

    @staticmethod
    def new_entry(blog_id, title, content, date=datetime.datetime.utcnow()):
        blog = Blog.from_mongo(blog_id)
        blog.new_entry(
            title=title,
            content=content,
            date=date
        )

    def json(self):
        return {
            "email": self.email,
            "_id": self._id,
            "password": self.password,
        }

    def save_to_db(self):
        Database.insert("users", self.json())

    def get_recent_posts(self, n):
        """
        Since `author` field in `entires` collection is the email-id of the user,\n
        which has been set to unique identifier in the `users` collecion, we can query\n
        for the entires using that field
        """
        list(Database.find("entries", {}, 'date', -1))
        return Database.find("entries", {'author': self.email}, 'date', -1).limit(n)

    def count_posts(self):
        return Database.count("entries", "author", self.email)

    def count_blogs(self):
        return Database.count("blogs", 'author', self.email)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def is_active(self):
        return True

    def get_id(self):
        return self._id
