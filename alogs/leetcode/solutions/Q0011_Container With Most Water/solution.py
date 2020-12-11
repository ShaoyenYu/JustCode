from typing import List


class Solution:
    def maxArea(self, height: List[int]) -> int:
        pass


class Solution01(Solution):
    def maxArea(self, height: List[int]) -> int:
        lptr, rptr = 0, len(height) - 1
        cum_max = 0
        while lptr < rptr:
            left, right = height[lptr], height[rptr]
            cur = (rptr - lptr) * min(left, right)
            cum_max = cur if cur > cum_max else cum_max
            if left < right:
                lptr += 1
            else:
                rptr -= 1
        return cum_max
