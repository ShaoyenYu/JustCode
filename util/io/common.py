import datetime as dt
import hashlib
import os
import pickle
import sys
import time
from functools import wraps


def log(f):
    module_name = os.path.basename(sys.argv[0])

    # mod = sys.modules["__main__"]
    # file = getattr(mod, '__file__', None)
    # module_name = file and os.path.splitext(os.path.basename(file))[0]

    @wraps(f)
    def wrapper(*args, **kwargs):
        print(f"TIME: {dt.datetime.now()}; SCRIPT_NAME: {module_name}; START;")
        res = f(*args, **kwargs)
        print(f"TIME: {dt.datetime.now()}; SCRIPT_NAME: {module_name}; Done;")

        return res

    return wrapper


def hash_clscache(cacheattr=None, paramhash=False, selfhash=False, maxcache=-1):
    """
        Cache decorator for class instance, with different level of cache strategy.
    Args:
        cacheattr: str
            instance attribute for storing cache;
        paramhash: bool, default False
            cache strategy. If True, when `func` is called with different parameters, all result will be cached;
        selfhash: bool, default False
            whether to use self as a parameter to generate cache key. If True, the instance should support __hash__
            method;
        maxcache: int, default -1
            max cache number of keys. Cache dict will clear if length of cache exceed this number.
            default -1, means no limit;
    """

    def _cache(func):
        cachewhere = cacheattr or "_" + func.__name__

        @wraps(func)
        def wrapper(this, *args, **kwargs):
            to_pickle = [func.__name__]
            if paramhash:
                to_pickle.extend([args, kwargs])
            if selfhash:
                to_pickle.append(hash(this))
            hash_key = hashlib.md5(pickle.dumps(tuple(to_pickle))).hexdigest()

            if hasattr(this, cachewhere):
                if hash_key not in getattr(this, cachewhere):
                    if 0 < maxcache <= len(getattr(this, cachewhere)):
                        getattr(this, cachewhere).clear()
                    getattr(this, cachewhere)[hash_key] = func(this, *args, **kwargs)
            else:
                setattr(this, cachewhere, {hash_key: func(this, *args, **kwargs)})

            return getattr(this, cachewhere)[hash_key]

        return wrapper

    return _cache


def unhash_clscache(prefix="_", suffix=""):
    def _cache(func):
        @wraps(func)
        def wrapper(this, *args, **kwargs):
            fn = prefix + func.__name__ + suffix
            if not hasattr(this, fn):
                setattr(this, fn, func(this, *args, **kwargs))

            return getattr(this, fn)

        return wrapper

    return _cache


def cache(func):
    cached = {}

    @wraps(func)
    def wrapper(*args, **kwargs):
        hash_key = hashlib.md5(pickle.dumps((args, kwargs))).hexdigest()
        if hash_key not in cached:
            cached[hash_key] = func(*args, **kwargs)
        return cached[hash_key]

    return wrapper


def auto_retry(retry_max=-1, sleep=2, exceptions=(Exception,), echo=False):
    """
    Retry
    Args:
        retry_max: int
            max retry times
        sleep: num, float
            interval between retries
        exceptions: Exception
            exceptions to catch and retry
        echo: bool
            echo error message

    Returns:

    """

    def _auto_retry(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            retry, res = 0, None
            while (retry_max < 0) or (retry <= retry_max):
                try:
                    return f(*args, **kwargs)
                except Exception as e:
                    if e in exceptions:
                        if echo:
                            print(f"retry: {retry}, args: {args}, error: {e}")
                        retry += 1
                        time.sleep(sleep)
                        continue
                    else:
                        return

        return wrapper

    return _auto_retry
