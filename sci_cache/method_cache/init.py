from .handlers import PickleCacheHandler, NumpyCacheHandler, PLYCacheHandler


def init():
    from sci_cache.method_cache.inner_cache import InnerCache


    try:
        import numpy
    except ImportError:
        numpy = None

    try:
        import open3d
    except ImportError:
        open3d = None

    InnerCache.register_handler(PickleCacheHandler())
    numpy and InnerCache.register_handler(NumpyCacheHandler())
    open3d and InnerCache.register_handler(PLYCacheHandler())

