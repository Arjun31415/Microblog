import os
import urllib
from pprint import pprint

from pymongo import MongoClient


class Database(object):

    """
    Wrapper around MongoDB database
    """
    URI = os.environ.get("MONGO_BASE")
    USER = urllib.parse.quote_plus(os.environ.get("MONGO_USER"))
    PWD = urllib.parse.quote_plus(os.environ.get("MONGO_PASSWORD"))
    REMAINING = os.environ.get("MONGO_REMAINING")
    DATABASE = None

    @staticmethod
    def initialize():
        client = MongoClient(
            Database.URI +
            Database.USER + ":" +
            Database.PWD +
            Database.REMAINING
        )
        Database.DATABASE = client.microblog
        print("database: ", Database.DATABASE)

    @staticmethod
    def insert(collection, data):
        Database.DATABASE[collection].insert(data)

    @staticmethod
    def find(collection, query, *sort_query):
        print("sort_query: ", sort_query)
        if sort_query == ():
            return Database.DATABASE[collection].find(query)
        print("sort_query: ", sort_query)
        return Database.DATABASE[collection].find(query).sort(*sort_query)

    @staticmethod
    def find_one(collection, query):
        return Database.DATABASE[collection].find_one(query)

    @staticmethod
    def count(collection, _id, val):
        pipeline = {_id: val}

        temp = Database.DATABASE[collection].find(pipeline)
        pprint(temp)
        return (len(list(temp)))

    @staticmethod
    def delete(collection, query):
        # try:
        #     Database.DATABASE[collection].remove(query)
        # except:
        #     print("Error in deleting ")
        Database.DATABASE[collection].remove(query)
