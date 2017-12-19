
class Solution:
    @classmethod
    def _setup(cls):
        pass

    @classmethod
    def _run(cls):
        cls.points_game()

    @classmethod
    def main(cls):
        cls._setup()
        cls._run()


class PointsGame1(Solution):
    @classmethod
    def points_game(cls, n: int):
        """
        Beauty of Programming 24点游戏(***, P103) Solution.1
        """
        if n == 1:
            if cls.nums[0] == cls.RESULT_VALUE:
                return True
            else:
                return False

        for i in range(n):
            for j in range(i + 1, n):
                a, b = cls.nums[i], cls.nums[j]
                expa, expb = cls.ress[i], cls.ress[j]

                cls.nums[j] = cls.nums[n - 1]
                cls.ress[j] = cls.ress[n - 1]

                cls.ress[i] = f"({expa}+{expb})"
                cls.nums[i] = a + b
                if cls.points_game(n - 1):
                    return True

                cls.ress[i] = f"({expa}-{expb})"
                cls.nums[i] = a - b
                if cls.points_game(n - 1):
                    return True

                cls.ress[i] = f"({expb}-{expa})"
                cls.nums[i] = b - a
                if cls.points_game(n - 1):
                    return True

                cls.ress[i] = f"({expa}*{expb})"
                cls.nums[i] = a * b
                if cls.points_game(n - 1):
                    return True

                if b != 0:
                    cls.ress[i] = f"({expa}/{expb})"
                    cls.nums[i] = a / b
                    if cls.points_game(n - 1):
                        return True

                if a != 0:
                    cls.ress[i] = f"({expb}/{expa})"
                    cls.nums[i] = b / a
                    if cls.points_game(n - 1):
                        return True

                cls.nums[i], cls.nums[j] = a, b
                cls.ress[i], cls.ress[j] = expa, expb

        return False

    @classmethod
    def _setup(cls):
        import numpy as np
        from array import array
        cls.CARD_NUMBER = 4
        cls.RESULT_VALUE = 24
        cls.case = np.random.randint(1, 14, size=4)
        cls.case = [1, 13, 8, 3]
        cls.nums = array("d", cls.case)
        cls.ress = list(cls.case)

    @classmethod
    def _run(cls):
        print(f"CASE:{cls.case}")
        print(f"RESULT: {cls.points_game(cls.CARD_NUMBER), cls.ress[0]}")


class PointsGame2(Solution):

    @classmethod
    def _setup(cls):
        import numpy as np
        cls.RESULTS = []
        cls.case = np.random.randint(1, 14, size=4)
        cls.case = [1, 13, 8, 3]

    @classmethod
    def _run(cls):
        print(cls.case)
        cls.points_game(cls.case)
        print(cls.RESULTS)

    @classmethod
    def points_game(cls, numbers, exprs=""):
        """所有解"""
        if len(numbers) == 1:
            if numbers[0] == 24:
                cls.RESULTS.append(exprs)
            else:
                pass

        length = len(numbers)
        for i in range(length):
            if length == 3:
                exprs = numbers[i]

            for j in range(i + 1, length):
                a, b = numbers[i], numbers[j]
                remain_list = [numbers[x] for x in range(length) if (x != i and x != j)]

                cls.points_game([a + b, *remain_list], f"({exprs}+{int(b)})")
                cls.points_game([a - b, *remain_list], f"({exprs}-{int(b)})")
                cls.points_game([a * b, *remain_list], f"({exprs}*{(b)})")
                if b != 0:
                    cls.points_game([a / b, *remain_list], f"({exprs}/{int(b)})")
                if a != 0:
                    cls.points_game([b / a, *remain_list], f"({int(b)}/{exprs})")


def main():
    PointsGame1.main()
    PointsGame2.main()


if __name__ == "__main__":
    main()
