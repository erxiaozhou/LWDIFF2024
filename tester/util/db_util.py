from config import MONGO_HOST, MONGO_PORT
from pymongo import MongoClient

'''
document
'''


mongo_host = MONGO_HOST
mongo_port = MONGO_PORT


def get_default_client():
    return MongoClient(MONGO_HOST, MONGO_PORT)


# def get_distinct_fields(collection):
#     return collection.distinct(None)
def get_distinct_fields(collection):
    distinct_fields = set()
    for document in collection.find():
        distinct_fields.update(document.keys())
    return list(distinct_fields)


def get_distinct_values(collection, field):
    return collection.distinct(field)
