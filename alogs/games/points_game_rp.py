import inspect
from collections import UserList


class Operator:
    def __init__(self, name, fn, num=None):
        self.name = name
        self.fn = fn
        self.num = num or len(inspect.signature(self.fn).parameters)  # inspect arg number of operator

    def __repr__(self):
        return f"{self.name}"


class ReversePolishStack(UserList):
    def __init__(self, init_list=None, finalize=False):
        init_list = init_list or []
        self.full_stacks = [*init_list]
        if finalize:
            init_list = self.finalize(init_list)
        super().__init__(init_list)

    @staticmethod
    def finalize(l):
        new_rpn_stack = ReversePolishStack()
        for element in l:
            new_rpn_stack.append(element)
        return new_rpn_stack

    def append(self, item) -> None:
        self.full_stacks.append(item)  # for tracking full stacks
        if isinstance(item, Operator):
            nums = (self.pop() for _ in range(item.num))
            item = item.fn(*tuple(nums)[::-1])
        super().append(item)

    @property
    def result(self):
        if len(self) != 1:
            res_maybe = self.finalize(self)
            return res_maybe[-1] if len(res_maybe) == 1 else None
        return self[-1]

    def __repr__(self):
        return " ".join((f"{x}" for x in self.full_stacks))


ops = {
    op.name: op
    for op in (
        Operator("+", lambda x, y: x + y),
        Operator("-", lambda x, y: x - y),
        Operator("*", lambda x, y: x * y),
        Operator("/", lambda x, y: x / y),
    )
}


def permutation_with_binary(numbers):
    # Combination of binary operators and numbers

    # Given number a, b, c, d, and token !;
    # Postfix Notation/ RPN(Reverse Polish Notation) <-> Infix Notation
    #   1) ab!c!d!  <->  (((a!b)!c)!d)
    #   2) ab!cd!！  <->  (((a!b)!c)!d)
    #   3) ab!c!d!  <->  (((a!b)!c)!d)
    #   4) ab!c!d!  <->  (((a!b)!c)!d)
    #   5) ab!c!d!  <->  (((a!b)!c)!d)
    pass


if __name__ == '__main__':
    a = ReversePolishStack([2, 5, ops["-"]], True)
    print(a.result)
    a = ReversePolishStack([1, 2, ops["+"], 4, ops["*"]], True)
    print(a.result)
    a = ReversePolishStack([1, 2, ops["+"], 4, ops["*"], 2, ops["*"]], True)
    print(a.result)
    a = ReversePolishStack([1, 2, ops["+"], 4, ops["*"], 2, ops["*"], 3], True)
    print(a.result)
    a = ReversePolishStack([1, 2, ops["+"], 4, ops["*"], 2, ops["*"], 3, ops["+"]], False)
    print(a.result)
