from typing import List


class Solution:
    def majorityElement(self, nums: List[int]) -> int:
        pass


class Solution01(Solution):
    def majorityElement(self, nums: List[int]) -> int:
        # using Boyer-Moore Voting Algorithm
        i, cur = 0, nums[0]
        for num in nums:
            if i == 0:
                i, cur = 1, num
            elif cur == num:
                i += 1
            else:
                i -= 1
        return num


class Solution02(Solution):
    def majorityElement(self, nums: List[int]) -> int:
        # using hash map to count
        count = {}
        threshold = len(nums) // 2 + 1
        for num in nums:
            val = count.get(num, 0) + 1
            if val == threshold:
                return num
            count[num] = val
