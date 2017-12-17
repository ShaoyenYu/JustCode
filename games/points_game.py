class PointsGame:
    @classmethod
    def setup(cls):
        pass

    @classmethod
    def points_gmae(cls):
        pass

    @classmethod
    def run(cls):
        cls.points_game()

    @classmethod
    def main(cls):
        cls.setup()
        cls.run()


class Solution1(PointsGame):
    @classmethod
    def setup(cls):
        import numpy as np
        from array import array
        cls.CARD_NUMBER = 4
        cls.RESULT_VALUE = 24
        cls.case = np.random.randint(1, 14, size=4)
        cls.nums = array("d", cls.case)
        cls.ress = list(cls.case)

    @classmethod
    def points_game(cls, n):
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
    def run(cls):
        print(f"CASE:{cls.case}")
        print(f"RESULT: {cls.points_game(cls.CARD_NUMBER), cls.ress[0]}")


class Solution2(PointsGame):
    @classmethod
    def points_game(cls, numbers, value):
        if len(numbers) == 1:
            if numbers[0] == 24:
                return True
            else:
                return False
        for i in range(len(numbers)):
            for j in range(i + 1, len(numbers)):
                a, b = numbers[i], numbers[j]


def main():
    Solution1.main()
    # Solution2.main()
