import datetime
import uuid

from database.db import Database


class Entry(object):
    """
    Class for user Entry
    """

    def __init__(self, blog_id, title, content, author, created_date=datetime.datetime.utcnow(), _id=None):
        self.blog_id = blog_id
        self.title = title
        self.content = content
        self.author = author
        self.created_date = created_date
        self._id = uuid.uuid4().hex if _id is None else _id

    def save_to_mongo(self):
        Database.insert(collection='entries',
                        data=self.json())

    def json(self):
        return {
            '_id': self._id,
            'blog_id': self.blog_id,
            'author': self.author,
            'content': self.content,
            'title': self.title,
            'created_date': self.created_date
        }

    @classmethod
    def from_mongo(cls, ID):
        post_data = Database.find_one(collection='entries', query={'_id': ID})
        return cls(**post_data)

    @staticmethod
    def from_blog(blog_id):
        return [post for post in Database.find(collection='entries', query={'blog_id': blog_id})]

    @classmethod
    def find_by_id(cls, _id):
        entry = Database.find(collection='entries', query={'_id': _id})
        return [cls(**entry) for entry in entry][0]

    def delete(self):
        Database.delete(collection='entries', query={'_id': self._id})
