import pickle
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class CacheHandler(ABC):
    """
    Abstract base class defining the interface for cache handlers.
    """

    def __init__(self, extension: str):
        """
        Initialize the cache handler.

        Args:
            extension (str): File extension, e.g., '.pickle', '.npy', '.ply'.
        """
        self.extension = extension.lower()

    @abstractmethod
    def check(self, value: Any) -> bool:
        """
        Check if the given value is suitable for this handler.

        Args:
            value (Any): The value to check.

        Returns:
            bool: True if the value is suitable for this handler, False otherwise.
        """
        pass

    @abstractmethod
    def read(self, path: Path) -> Any:
        """
        Read data from a file.

        Args:
            path (Path): The file path.

        Returns:
            Any: The data read from the file.
        """
        pass

    @abstractmethod
    def write(self, path: Path, value: Any) -> None:
        """
        Write data to a file.

        Args:
            path (Path): The file path.
            value (Any): The data to write.
        """
        pass


class PickleCacheHandler(CacheHandler):
    """
    Cache handler for dictionary types using pickle for serialization.
    """

    def __init__(self):
        super().__init__(extension=".pickle")

    def check(self, value: Any) -> bool:
        return isinstance(value, dict)

    def read(self, path: Path) -> Any:
        with path.open("rb") as f:
            return pickle.load(f)

    def write(self, path: Path, value: Any) -> None:
        with path.open("wb") as f:
            pickle.dump(value, f)


class NumpyCacheHandler(CacheHandler):
    """
    Cache handler for NumPy array types using numpy.save and numpy.load.
    """

    def __init__(self):
        super().__init__(extension=".npy")

    def check(self, value: Any) -> bool:
        import numpy as np
        return isinstance(value, np.ndarray)

    def read(self, path: Path) -> Any:
        import numpy as np
        return np.load(path, allow_pickle=True)

    def write(self, path: Path, value: Any) -> None:
        import numpy as np
        np.save(path, value)


class PLYCacheHandler(CacheHandler):
    """
    Cache handler for Open3D point cloud types using Open3D's read and write functions.
    """

    def __init__(self):
        super().__init__(extension=".ply")

    def check(self, value: Any) -> bool:
        import open3d as o3d
        return isinstance(value, o3d.geometry.PointCloud)

    def read(self, path: Path) -> Any:
        import open3d as o3d
        return o3d.io.read_point_cloud(str(path))

    def write(self, path: Path, value: Any) -> None:
        import open3d as o3d
        o3d.io.write_point_cloud(str(path), value)
