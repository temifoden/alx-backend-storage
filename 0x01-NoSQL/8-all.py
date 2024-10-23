#!/usr/bin/env python3
"""List all documents in a collection"""


def list_all(mongo_collection):
    """List all document in a collectiton"""
    document = mongo_collection.find()
    return document
