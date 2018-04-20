try:
    # Python 3.2+
    from functools import lru_cache
except ImportError:
    from pylru import lrudecorator as lru_cache

