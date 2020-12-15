from typing import List


class Solution:
    def majorityElement(self, nums: List[int]) -> int:
        pass


class Solution01(Solution):
    def majorityElement(self, nums: List[int]) -> int:
        i, cur = 0, nums[0]
        for num in nums:
            if cur == num:
                i += 1
            else:
                i -= 1

            if i == 0:
                cur = num
                i += 1
        return cur
