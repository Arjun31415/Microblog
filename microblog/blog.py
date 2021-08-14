import datetime
from os import stat
import uuid

from database.db import Database
from entry import Entry


class Blog(object):
    """
    A page of the user where entries are made\n
    This class makes a wrapper around it and also communicates to the Database
    """

    def __init__(self, author, title, description, author_id, _id=None):
        self.author = author
        self.author_id = author_id
        self.title = title
        self.description = description
        self._id = uuid.uuid4().hex if _id is None else _id

    def new_entry(self, title, content, date=datetime.datetime.utcnow()):
        entry = Entry(
            blog_id=self._id,
            title=title,
            content=content,
            author=self.author,
            created_date=date
        )
        entry.save_to_mongo()

    def get_id(self):
        return self._id

    def get_posts(self):
        return Entry.from_blog(self._id)

    def save_to_mongo(self):
        Database.insert(
            collection='blogs',
            data=self.json()
        )

    def json(self):
        return {
            'author': self.author,
            'author_id': self.author_id,
            'title': self.title,
            'description': self.description,
            '_id': self._id
        }

    @classmethod
    def from_mongo(cls, _id):
        blog_data = Database.find_one(
            collection='blogs',
            query={'_id': _id}
        )
        return cls(**blog_data)

    @classmethod
    def find_by_author_id(cls, author_id):
        blogs = Database.find(
            collection='blogs',
            query={'author_id': author_id}
        )
        return [cls(**blog) for blog in blogs]

    @classmethod
    def find_by_id(cls, _id):
        blog = Database.find(collection='blogs', query={'_id': _id})
        return [cls(**blog) for blog in blog][0]

    def delete(self):
        Database.delete(collection='blogs', query={'_id': self._id})
        Database.delete(collection='entries', query={'blog_id': self._id})
