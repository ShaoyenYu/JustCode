class Solution:
    def isPalindrome(self, x: int) -> bool:
        pass


class Solution01(Solution):
    # use double pointer
    def isPalindrome(self, x: int) -> bool:
        if 0 <= x < 10:  # prune: integer less than 10
            return True
        if (x < 0) or (x % 10 == 0):  # prune: negative number, and multiples of ten
            return False

        right = 0
        while right < x:
            right = right * 10 + x % 10
            if x == right:
                return True
            x //= 10
        return x == right


class Solution02(Solution):
    # simply reverse integer
    def isPalindrome(self, x: int):
        if x < 0:
            return False

        left, right = x, 0
        while left > 0:
            right = right * 10 + left % 10
            left //= 10
        return right == x


if __name__ == '__main__':
    solutions = [Solution01, Solution02]
    test_cases = [(1231, False), (1001, True), (101, True), (0, True), (10, False)]
    for solution in solutions:
        for case in test_cases:
            assert getattr(solution, "isPalindrome")(solution, case[0]) is case[1]
