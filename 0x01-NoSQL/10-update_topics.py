#!/usr/bin/env python3
""" update document data in a collection"""


def update_topics(mongo_collection, name, topics):
    """ update document data"""
    query = {name: name}
    value = {"$set" : {topics: topics}}
    optional = {"multi": true}
    document = mongo_collection.update(query, value, optional)
    return document
