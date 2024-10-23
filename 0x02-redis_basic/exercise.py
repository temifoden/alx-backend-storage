#!/usr/bin/env python3
"""Cache class with Redis and call history tracking"""
import redis
import uuid
from typing import Union, Callable, Optional
import functools


def call_history(method: Callable) -> Callable:
    """
    A decorator that stores the input arguments and output of a function in Redis.

    Args:
        method (Callable): The method to be decorated.

    Returns:
        Callable: The wrapped method with input/output logging.
    """
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        """Wrapper function to log inputs and outputs in Redis."""
        input_key = f"{method.__qualname__}:inputs"
        output_key = f"{method.__qualname__}:outputs"

        # Store the input arguments in the 'inputs' list
        self._redis.rpush(input_key, str(args))

        # Call the original method and capture its output
        output = method(self, *args, **kwargs)

        # Store the output in the 'outputs' list
        self._redis.rpush(output_key, str(output))

        # Return the output
        return output

    return wrapper


def count_calls(method: Callable) -> Callable:
    """
    A decorator that counts how many times a method is called using Redis.

    Args:
        method (Callable): The method to be decorated.

    Returns:
        Callable: The wrapped method with call counting.
    """
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        """Wrapper function to increment the call count in Redis."""
        key = method.__qualname__
        self._redis.incr(key)
        return method(self, *args, **kwargs)

    return wrapper


class Cache:
    def __init__(self):
        """Initialize the Cache class with a Redis instance and flush the DB."""
        self._redis = redis.Redis()
        self._redis.flushdb()

    @call_history  # Decorate with call_history to log inputs and outputs
    @count_calls   # Decorate with count_calls to count how many times store is called
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
        data = self._redis.get(key)
        if data is None:
            return None
        return fn(data) if fn else data

    def get_str(self, key: str) -> Optional[str]:
        """Retrieve a string value from Redis."""
        return self.get(key, lambda d: d.decode("utf-8"))

    def get_int(self, key: str) -> Optional[int]:
        """Retrieve an integer value from Redis."""
        return self.get(key, lambda d: int(d))


if __name__ == "__main__":
    # Example usage
    cache = Cache()

    # Storing data
    s1 = cache.store("first")
    print(s1)
    s2 = cache.store("second")
    print(s2)
    s3 = cache.store("third")
    print(s3)

    # Retrieve the input/output history from Redis
    inputs = cache._redis.lrange(f"{cache.store.__qualname__}:inputs", 0, -1)
    outputs = cache._redis.lrange(f"{cache.store.__qualname__}:outputs", 0, -1)

    print("inputs: {}".format(inputs))
    print("outputs: {}".format(outputs))
