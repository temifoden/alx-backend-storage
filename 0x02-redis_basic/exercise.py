#!/usr/bin/env python3
"""Cache class with Redis and call history replay"""
import redis
import uuid
from typing import Union, Callable, Optional
import functools


def call_history(method: Callable) -> Callable:
    """Stores the history of inputs and outputs for a particular function in Redis."""
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        """Wrapper to log inputs and outputs in Redis."""
        input_key = f"{method.__qualname__}:inputs"
        output_key = f"{method.__qualname__}:outputs"

        # Store the input arguments
        self._redis.rpush(input_key, str(args))

        # Call the original method and get its result
        result = method(self, *args, **kwargs)

        # Store the output
        self._redis.rpush(output_key, str(result))

        return result

    return wrapper


def count_calls(method: Callable) -> Callable:
    """Counts how many times a method is called."""
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        """Wrapper to count function calls in Redis."""
        self._redis.incr(method.__qualname__)
        return method(self, *args, **kwargs)

    return wrapper


def replay(method: Callable):
    """
    Display the history of calls to a particular function.
    
    Args:
        method (Callable): The function whose call history we want to display.
    """
    # Get the qualified name of the method to form the Redis keys
    input_key = f"{method.__qualname__}:inputs"
    output_key = f"{method.__qualname__}:outputs"

    # Retrieve the inputs and outputs from Redis
    redis_instance = method.__self__._redis
    inputs = redis_instance.lrange(input_key, 0, -1)
    outputs = redis_instance.lrange(output_key, 0, -1)

    # Count the number of calls
    num_calls = len(inputs)

    # Print the call history
    print(f"{method.__qualname__} was called {num_calls} times:")

    # Iterate over the zipped inputs and outputs
    for input_args, output in zip(inputs, outputs):
        input_args_str = input_args.decode("utf-8")
        output_str = output.decode("utf-8")
        print(f"{method.__qualname__}(*{input_args_str}) -> {output_str}")


class Cache:
    def __init__(self):
        """Initialize the Cache class with a Redis instance."""
        self._redis = redis.Redis()
        self._redis.flushdb()

    @call_history
    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store the data in Redis with a randomly generated key and return the key.
        
        Args:
            data (Union[str, bytes, int, float]): The data to store.
        
        Returns:
            str: The key where the data is stored.
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Optional[Callable] = None) -> Optional[Union[str, bytes, int]]:
        """Retrieve data from Redis."""
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

    # Store some values
    cache.store("foo")
    cache.store("bar")
    cache.store(42)

    # Replay the call history
    replay(cache.store)
