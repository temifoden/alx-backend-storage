import redis
import uuid
from typing import Callable, Union, Optional
import functools


def count_calls(method: Callable) -> Callable:
    """
    A decorator that counts how many times a method is called using Redis.

    Args:
        method (Callable): The method to be decorated.

    Returns:
        Callable: The wrapped method with call counting.
    """
    @functools.wraps(method)  # Preserve the original method's metadata (name, docstring, etc.)
    def wrapper(self, *args, **kwargs):
        """Wrapper function to increment the call count in Redis."""
        # Increment the call count for the method's qualified name
        key = method.__qualname__
        self._redis.incr(key)
        # Call the original method and return its result
        return method(self, *args, **kwargs)

    return wrapper


class Cache:
    def __init__(self):
        """Initialize the Cache class with a Redis instance and flush the DB."""
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls  # Decorate the store method to count its calls
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
    cache.store(b"first")
    print(cache.get(cache.store.__qualname__))  # Should print: b'1'

    cache.store(b"second")
    cache.store(b"third")
    print(cache.get(cache.store.__qualname__))  # Should print: b'3'
