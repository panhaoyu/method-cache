# sci-cache

A Python library for caching scientific data on disk, streamlining research workflows by storing intermediate results.

## Features

- **Method-Based Caching**: Automatically cache each method's result based on the method name to the specified directory.
- **Easy Integration**: Inherit from `MethodDiskCache` and use the `@sci_method_cache` decorator to enable caching.
- **Flexible Storage**: Store cached data in a designated folder, organized and managed automatically.
- **Supports Various Data Types**: Ideal for scientific data processing tasks, handling complex data types efficiently.

## Installation

```bash
pip install sci-cache
```

## Usage

```python
from pathlib import Path

from sci_cache import MethodDiskCache, sci_method_cache


# Define a caching class by inheriting from MethodDiskCache
class ScientificCache(MethodDiskCache):
    compute_square_count = 0  # Track compute_square calls
    compute_cube_count = 0  # Track compute_cube calls

    def get_cache_folder(self) -> Path:
        # Set the cache directory to 'cache' folder in the current script's directory
        return Path(__file__).parent / "cache"

    @sci_method_cache
    def compute_square(self) -> int:
        # Increment the count to track actual computation
        ScientificCache.compute_square_count += 1
        return 3 * 3  # Example computation

    @sci_method_cache
    def compute_cube(self) -> int:
        # Increment the count to track actual computation
        ScientificCache.compute_cube_count += 1
        return 2 * 2 * 2  # Example computation


# Instantiate the caching class and use the cached methods
cache1 = ScientificCache()

# First call: performs computation and caches the result
square1 = cache1.compute_square()
assert square1 == 9
assert ScientificCache.compute_square_count == 1

# Second call: retrieves the result from cache without recomputing
square2 = cache1.compute_square()
assert square2 == 9
assert ScientificCache.compute_square_count == 1

# First call: performs computation and caches the result
cube1 = cache1.compute_cube()
assert cube1 == 8
assert ScientificCache.compute_cube_count == 1

# Second call: retrieves the result from cache without recomputing
cube2 = cache1.compute_cube()
assert cube2 == 8
assert ScientificCache.compute_cube_count == 1

# Re-instantiate the caching class to simulate a new session
cache2 = ScientificCache()

# Call methods again to ensure cached results are used
square3 = cache2.compute_square()
assert square3 == 9
assert ScientificCache.compute_square_count == 1

cube3 = cache2.compute_cube()
assert cube3 == 8
assert ScientificCache.compute_cube_count == 1

print("All assertions passed.")
```

## License

MIT License. See [LICENSE](./LICENSE) for more information.
