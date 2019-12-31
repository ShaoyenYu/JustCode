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
            ################################################################
            # stack trace
            to_prints = {
                "n": f"{str(int(n)):3}",
                "-": "-" * 80,
                "nums": f"{str(list(cls.nums)):38}",
                "exps": f"{str(list(cls.ress)):25}",
            }
            to_prints = "|  ".join((f"{k}: {v}" for k, v in to_prints.items()))
            print(to_prints)
            ################################################################

            if cls.nums[0] == cls.RESULT_VALUE:
                cls.allress.append(cls.ress[0])
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

                ################################################################
                # stack trace
                to_prints = {
                    "n": f"{str(int(n)):3}",
                    "i": f"{str(int(i)):3}",
                    "j": f"{str(int(j)):3}",
                    "a": f"{str(a)[:4]:6}",
                    "b": f"{str(b)[:4]:6}",
                    "expa": f"{str(expa):13}",
                    "expb": f"{str(expb):13}",
                    "nums": f"{str(list(cls.nums)):38}",
                    "exps": f"{str(list(cls.ress)):25}",
                }
                to_prints = "|  ".join((f"{k}: {v}" for k, v in to_prints.items()))
                print(to_prints)
                ################################################################

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

                ################################################################
                # stack trace
                to_prints = {
                    "n": f"{str(int(n)):3}",
                    "i": f"{str(int(i)):3}",
                    "j": f"{str(int(j)):3}",
                    "a": f"{str(a)[:4]:6}",
                    "b": f"{str(b)[:4]:6}",
                    "expa": f"{str(expa):13}",
                    "expb": f"{str(expb):13}",
                    "nums": f"{str(list(cls.nums)):38}",
                    "exps": f"{str(list(cls.ress)):25}",
                }
                to_prints = "|  ".join((f"{k}: {v}" for k, v in to_prints.items()))
                print(to_prints)
                ################################################################

        return False

    @classmethod
    def _setup(cls):
        import numpy as np
        from array import array
        cls.CARD_NUMBER = 4
        cls.RESULT_VALUE = 24
        cls.case = np.random.randint(1, 14, size=4)
        cls.case = [1, 2, 3, 4]
        cls.nums = array("d", cls.case)
        cls.ress = list(cls.case)
        cls.allress = []

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
    # PointsGame2.main()


if __name__ == "__main__":
    main()
