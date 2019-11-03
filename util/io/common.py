import time
from functools import wraps


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
