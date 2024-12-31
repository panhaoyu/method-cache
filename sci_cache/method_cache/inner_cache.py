import re
from collections import UserDict
from pathlib import Path
from typing import List, Any, Optional, Iterator

from pypinyin import lazy_pinyin

from .handlers import CacheHandler


class InnerCache(UserDict):
    """
    Internal cache class managing read and write operations for cache files.
    Supports extending different data type handlers by registering CacheHandler subclasses.
    """

    # Class attribute: list of handlers
    handlers: List[CacheHandler] = []

    @classmethod
    def register_handler(cls, handler: CacheHandler) -> None:
        """
        Register a handler for a specific data type.

        The first registered handler will be used as the default handler.
        The last registered handler will be checked first.
        Thus, user can register new handlers to override existing ones.

        Args:
            handler (CacheHandler): An instance of a CacheHandler subclass.
        """
        # Ensure each extension is unique
        if any(existing_handler.extension == handler.extension for existing_handler in cls.handlers):
            raise ValueError(f"Extension '{handler.extension}' is already registered.")
        cls.handlers.insert(0, handler)

    def __init__(self, path: Path):
        super().__init__()
        self.path = path
        self.path.mkdir(parents=True, exist_ok=True)

    def get_ascii_name(self, name: str) -> str:
        """
        Convert the name to ASCII format suitable for filenames.

        Args:
            name (str): The original name.

        Returns:
            str: The ASCII-formatted name.
        """
        ascii_name = '_'.join(lazy_pinyin(name))
        ascii_name = re.sub(r'_+', '_', ascii_name).strip('_')
        return ascii_name

    def get_new_file_path(self, name: str, value: Any) -> Path:
        """
        Generate a new cache file path based on the name and data type.

        Args:
            name (str): The cache key name.
            value (Any): The cache value.

        Returns:
            Path: The new cache file path.
        """
        ascii_name = self.get_ascii_name(name)
        handler = self.get_handler_for_value(value)
        if handler is None:
            raise ValueError(f"Unsupported type for value: {type(value)}")
        return self.path / f"{ascii_name}{handler.extension}"

    def get_handler_for_value(self, value: Any) -> Optional[CacheHandler]:
        """
        Get the appropriate handler for the given value.

        Args:
            value (Any): The value.

        Returns:
            Optional[CacheHandler]: The corresponding handler if found, else None.
        """
        for handler in self.handlers:
            if handler.check(value):
                return handler
        return self.handlers[-1]

    def get_existing_file_path(self, name: str) -> Optional[Path]:
        """
        Get the existing cache file path for the given name.

        Args:
            name (str): The cache key name.

        Returns:
            Optional[Path]: The existing file path if found, else None.
        """
        ascii_name = self.get_ascii_name(name)
        matched_files = []
        for handler in self.handlers:
            matched_files.extend(self.path.glob(f"{ascii_name}{handler.extension}"))
        if len(matched_files) > 1:
            raise FileExistsError(f"Multiple cache files found for key '{name}'.")
        return matched_files[0] if matched_files else None

    def get_cache_file_path(self, name: str, value: Any = None) -> Path:
        """
        Get the cache file path, creating a new one if it doesn't exist.

        Args:
            name (str): The cache key name.
            value (Any, optional): The cache value to determine the file type.

        Returns:
            Path: The cache file path.
        """
        existing_path = self.get_existing_file_path(name)
        if existing_path is not None:
            return existing_path
        if value is None:
            raise KeyError(f"No cache found for key '{name}'.")
        return self.get_new_file_path(name, value)

    def __contains__(self, item: str) -> bool:
        """
        Check if the cache contains the specified key.

        Args:
            item (str): The key name.

        Returns:
            bool: True if the key exists, False otherwise.
        """
        return self.get_existing_file_path(item) is not None

    def __getitem__(self, item: str) -> Any:
        """
        Retrieve the cached value for the specified key.

        Args:
            item (str): The key name.

        Returns:
            Any: The cached value.
        """
        path = self.get_cache_file_path(item)
        suffix = path.suffix.lower()
        handler = self.get_handler_for_extension(suffix)
        if handler is None:
            raise ValueError(f'Unsupported file extension "{suffix}" for key "{item}".')
        return handler.read(path)

    def __setitem__(self, key: str, value: Any) -> None:
        """
        Set the cached value for the specified key.

        Args:
            key (str): The key name.
            value (Any): The value to cache.
        """
        path = self.get_cache_file_path(key, value)
        handler = self.get_handler_for_value(value)
        if handler is None:
            raise ValueError(f"Unsupported type for value: {type(value)}")
        handler.write(path, value)

    def __delitem__(self, key: str) -> None:
        """
        Delete the cached file for the specified key.

        Args:
            key (str): The key name.
        """
        path = self.get_cache_file_path(key)
        try:
            path.unlink()
        except FileNotFoundError:
            raise KeyError(f"No cache found for key '{key}' to delete.")

    def __iter__(self) -> Iterator[str]:
        """
        Iterate over all cache keys.

        Yields:
            Iterator[str]: The cache key names.
        """
        seen = set()
        for handler in self.handlers:
            pattern = f"*{handler.extension}"
            for file in self.path.glob(pattern):
                if file.stem not in seen:
                    seen.add(file.stem)
                    yield file.stem

    def get_handler_for_extension(self, extension: str) -> Optional[CacheHandler]:
        """
        Get the handler corresponding to the given file extension.

        Args:
            extension (str): The file extension.

        Returns:
            Optional[CacheHandler]: The corresponding handler if found, else None.
        """
        for handler in self.handlers:
            if handler.extension == extension:
                return handler
        return None
