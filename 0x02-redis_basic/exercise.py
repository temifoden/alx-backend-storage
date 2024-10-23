import redis
import uuid
from typing import Union


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


if __name__ == "__main__":
    # Example usage
    cache = Cache()

    data = b"hello"  # Data to be stored
    key = cache.store(data)  # Store the data and get the generated key
    print(key)  # Print the generated key

    # Retrieve the data from Redis to verify
    local_redis = redis.Redis()
    print(local_redis.get(key))  # Should output: b'hello'
