def is_mirror(num, n=0):
    s_num = str(num)
    num_rev = int(s_num[::-1])
    s = num + num_rev
    if n % 100 == 0:
        print(n, num, s)
    if (s - int(str(s)[::-1])) == 0:
        print(n, num, s)
        return num
    return is_mirror(s, n + 1)


is_mirror(196)

for i in range(int(1e9)):
    print(i)
    try:
        is_mirror(i)
    except RecursionError:
        break

import Levenshtein
s1 = "I love you li wvvvw.51job.com try".lower()
s2 = "l Iove you h wwwv.s1j0b.eom fry".lower()

m = {
    "i": "1",
    "f": "t",
    "v": "w",
    "s": "5",
    "w": "vv",
    "l": "i",
    "h": "li",
}

Levenshtein.distance()
