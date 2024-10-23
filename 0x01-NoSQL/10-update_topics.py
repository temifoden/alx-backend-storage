#!/usr/bin/env python3
""" update document data in a collection"""


def update_topics(mongo_collection, name, topics):
    """ update document data"""
    query = {name: name}
    new_value = {"$set" : {topics: topics}}

    document = mongo_collection.update_many(query, new_value)
    return document
