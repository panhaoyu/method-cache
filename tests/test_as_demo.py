import tempfile
from pathlib import Path

from sci_cache import method_cache, MethodDiskCache


class ScientificCache(MethodDiskCache):
    compute_square_count = 0
    compute_cube_count = 0
    _temp_dir = None

    def get_cache_folder(self) -> Path:
        if ScientificCache._temp_dir is None:
            ScientificCache._temp_dir = tempfile.TemporaryDirectory()
        return Path(ScientificCache._temp_dir.name)

    @method_cache
    def compute_square(self) -> int:
        ScientificCache.compute_square_count += 1
        return 3 * 3

    @method_cache
    def compute_cube(self) -> int:
        ScientificCache.compute_cube_count += 1
        return 2 * 2 * 2


def test_cache():
    cache1 = ScientificCache()

    square1 = cache1.compute_square()
    assert square1 == 9
    assert ScientificCache.compute_square_count == 1

    square2 = cache1.compute_square()
    assert square2 == 9
    assert ScientificCache.compute_square_count == 1

    cube1 = cache1.compute_cube()
    assert cube1 == 8
    assert ScientificCache.compute_cube_count == 1

    cube2 = cache1.compute_cube()
    assert cube2 == 8
    assert ScientificCache.compute_cube_count == 1

    cache2 = ScientificCache()

    square3 = cache2.compute_square()
    assert square3 == 9
    assert ScientificCache.compute_square_count == 1

    cube3 = cache2.compute_cube()
    assert cube3 == 8
    assert ScientificCache.compute_cube_count == 1

    print("All assertions passed.")
