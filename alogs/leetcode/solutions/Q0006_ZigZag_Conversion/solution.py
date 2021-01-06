class Solution:
    def convert(self, s: str, numRows: int) -> str:
        pass


class Solution01(Solution):
    def convert(self, s: str, numRows: int) -> str:
        if numRows == 1 or len(s) < numRows:
            return s
        rows = [""] * numRows
        ptr_row, direction = 0, 1  # solve with pointer
        for i in range(len(s)):
            rows[ptr_row] += s[i]
            ptr_row += direction
            if ptr_row == numRows - 1 or ptr_row == 0:
                direction *= -1
        return "".join(rows)


class Solution02(Solution):
    def convert(self, s: str, numRows: int) -> str:
        if numRows == 1:
            return s

        step = numRows * 2 - 2
        rows = [""] * numRows

        for i in range(len(s)):  # pure math solution
            rows[min(i % step, step - i % step)] += s[i]

        return "".join(rows)
