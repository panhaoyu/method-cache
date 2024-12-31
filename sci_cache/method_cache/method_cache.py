import functools
import types
from abc import ABC, abstractmethod
from collections import UserDict
from functools import cached_property
from pathlib import Path
from typing import Union, Dict, Any, Callable

from .inner_cache import InnerCache


class MethodCache(ABC):
    @abstractmethod
    def get_cache_folder(self) -> Path:
        """
        Get the path to the cache folder.

        Returns:
            Path: The cache folder path.
        """
        raise NotImplementedError

    @cached_property
    def cache_dict(self) -> Union[Dict[str, Any], UserDict]:
        """
        Cache dictionary for storing and retrieving cached data.

        Returns:
            Union[Dict[str, Any], UserDict]: The cache dictionary instance.
        """
        raise NotImplementedError


class MethodDiskCache(MethodCache, ABC):
    @abstractmethod
    def get_cache_folder(self) -> Path:
        """
        Get the path to the cache folder.

        Returns:
            Path: The cache folder path.
        """
        pass

    def _initialize_cache(self) -> InnerCache:
        """
        Initialize the cache dictionary.

        Returns:
            InnerCache: An instance of InnerCache.
        """
        return InnerCache(self.get_cache_folder())

    @cached_property
    def cache_dict(self) -> InnerCache:
        """
        Cache dictionary for storing and retrieving cached data.

        Returns:
            InnerCache: The InnerCache instance.
        """
        return self._initialize_cache()


def sci_method_cache(func: Callable) -> Callable:
    """
    Decorator to cache the results of class methods.

    Only supports methods without parameters and requires the method's class to be a subclass of MethodCache.

    The prefix `sci_` is used to avoid the identifier duplicated with the `importlib.metadata.method_cache`.

    Args:
        func (Callable): The method to decorate.

    Returns:
        Callable: The wrapped method with caching functionality.
    """
    if not isinstance(func, (types.FunctionType,)):
        raise TypeError(f"@method_cache can only be applied to functions, got {type(func)}")

    key = func.__name__

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if len(args) != 1 or kwargs:
            raise ValueError("Only methods without parameters are supported.")

        self_instance: MethodCache = args[0]
        if not isinstance(self_instance, MethodCache):
            raise TypeError("The first argument must be an instance of MethodCache.")

        cache = self_instance.cache_dict

        if key in cache:
            return cache[key]

        result = func(self_instance)
        cache[key] = result
        return result

    return wrapper
