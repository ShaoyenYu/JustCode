
CARD_NUMBER = 4
RESULT_VALUE = 24

numbers = [13, 5, 7, 3]
results = [None, None, None, None]


def points_game(n):
    if n == 1:
        if numbers[0] == RESULT_VALUE:
            return True
        else:
            return False

    for i in range(n):
        for j in range(i+1, n):
            a, b = numbers[i], numbers[j]
            expa, expb = results[i], results[j]

            numbers[j] = numbers[n - 1]
            results[j] = results[n - 1]

            results[i] = f"({expa}+{expb})"
            numbers[i] = a + b
            if points_game(n - 1):
                return True

            results[i] = f"({expb}-{expa})"
            numbers[i] = b - 1
            if points_game(n - 1):
                return True

            results[i] = f"({expa}*{expb})"
            numbers[i] = a * b
            if points_game(n - 1):
                return True

            if b != 0:
                results[i] = f"({expa}/{expb})"
                numbers[i] = a / b
                if points_game(n - 1):
                    return True

            if a != 0:
                results[i] = f"({expb}/{expa})"
                numbers[i] = b / a
                if points_game(n - 1):
                    return True

            numbers[i], numbers[j] = a, b
            results[i], results[j] = expa, expb

    return False

points_game(4)
results