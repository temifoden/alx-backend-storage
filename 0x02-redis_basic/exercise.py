#!/usr/bin/env python3
"""Initialixe the cache class with a redis instance""" 
import redis
import uuid
from typing import Union, Callable, Optional


class Cache:
    def __init__(self):
        """Initialize the Cache class with a Redis instance and flush the DB."""
        self._redis = redis.Redis()
        self._redis.flushdb()  # Flush all data from Redis

    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store the data in Redis with a randomly generated key and return the key.

        Args:
            data (str, bytes, int, float): The data to be stored.

        Returns:
            str: The key under which the data is stored in Redis.
        """
        key = str(uuid.uuid4())  # Generate a random UUID as the key
        self._redis.set(key, data)  # Store the data in Redis with the generated key
        return key

    def get(self, key: str, fn: Optional[Callable] = None) -> Optional[Union[str, bytes, int]]:
        """
        Retrieve data from Redis using the given key and apply a transformation if fn is provided.

        Args:
            key (str): The key to look up in Redis.
            fn (Callable, optional): A function to convert the data back to the desired format.

        Returns:
            Optional[Union[str, bytes, int]]: The data retrieved from Redis, transformed by fn if provided.
        """
        data = self._redis.get(key)  # Get the data from Redis
        if data is None:
            return None  # Return None if key doesn't exist
        return fn(data) if fn else data  # Apply the transformation if fn is provided, otherwise return raw data

    def get_str(self, key: str) -> Optional[str]:
        """
        Retrieve a string value from Redis.

        Args:
            key (str): The key to look up in Redis.

        Returns:
            Optional[str]: The string data, or None if the key doesn't exist.
        """
        return self.get(key, lambda d: d.decode("utf-8"))

    def get_int(self, key: str) -> Optional[int]:
        """
        Retrieve an integer value from Redis.

        Args:
            key (str): The key to look up in Redis.

        Returns:
            Optional[int]: The integer data, or None if the key doesn't exist.
        """
        return self.get(key, lambda d: int(d))



if __name__ == "__main__":
    # Example usage
    cache = Cache()

    # Test cases as per the problem statement
    TEST_CASES = {
        b"foo": None,
        123: int,
        "bar": lambda d: d.decode("utf-8")
    }

    for value, fn in TEST_CASES.items():
        key = cache.store(value)
        assert cache.get(key, fn=fn) == value

    print("All test cases passed.")