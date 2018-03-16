import sys


# Real Tail Recursion Optimization
class TailRecurseException(BaseException):
    def __init__(self, args, kwargs):
        self.args = args
        self.kwargs = kwargs


def tail_call_optimized(g):
    """
    This function decorates a function with tail call
    optimization. It does this by throwing an exception
    if it is its own grandparent, and catching such
    exceptions to fake the tail call optimization.

    This function fails if the decorated
    function recurses in a non-tail context.
    """

    def func(*args, **kwargs):
        f = sys._getframe()
        if f.f_back and f.f_back.f_back and f.f_back.f_back.f_code == f.f_code:
            raise TailRecurseException(args, kwargs)
        else:
            while 1:
                try:
                    return g(*args, **kwargs)
                except TailRecurseException as e:
                    args = e.args
                    kwargs = e.kwargs

    return func


# Cache Optimization
def cache(g):
    cached = {}

    def wraps(*args):
        if args not in cached:
            cached[args] = g(*args)
        return cached[args]
    return wraps


# test func1
def recsum(x):
    if x == 1:
        return x
    return x + recsum(x - 1)


@tail_call_optimized
def recsum_to(x, s=0):
    if x == 1:
        return 1 + s
    return recsum_to(x - 1, x + s)


# test func2
def fib(x):
    if x < 3:
        return 1
    return fib(x - 1) + fib(x - 2)


@tail_call_optimized
def fib_to(x, prev_1=0, prev_2=1):
    if x == 0:
        return prev_1
    return fib_to(x - 1, prev_2, prev_1 + prev_2)


@cache
def fib_cc(x):
    if x < 3:
        return 1
    return fib_cc(x - 1) + fib_cc(x - 2)


@cache
@tail_call_optimized
def fib_ccto(x, prev_1=0, prev_2=1):
    if x == 0:
        return prev_1
    return fib_to(x - 1, prev_2, prev_1 + prev_2)


def test():
    recsum_to(5)
    recsum(5)

    fib(30)  # 1.48ms
    fib_to(30)  # 55 us, O(n) stack-depth
    fib_cc(30)  # 181 ns, O(n) stack-depth
    fib_ccto(30)  # 180ns, O(1) stack-depth
