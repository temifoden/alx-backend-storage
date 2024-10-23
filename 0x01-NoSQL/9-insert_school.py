#!/usr/bin/env python3
def insert_school(mongo_collection, **kwargs):
    """
    Inserts a document into a collection
    :param mongo_collection: The pymongo collection object
    :kwargs: Arbitrary keyword arguments representing the document fields
    :return: The new document's _id
    """
    document_id = mongo_collection.insert(kwargs)
    return document_id
