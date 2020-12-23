from typing import List


class Solution:
    def removeDuplicates(self, nums: List[int]) -> int:
        pass


class Solution01(Solution):
    def removeDuplicates(self, nums: List[int]) -> int:
        # two pointer
        cur_idx, next_idx, max_len = 0, 1, len(nums)
        while next_idx < max_len:
            if nums[cur_idx] == nums[next_idx]:
                next_idx += 1
            else:
                cur_idx += 1
                nums[cur_idx] = nums[next_idx]
                next_idx += 1
        return cur_idx + 1


class Solution02(Solution):
    def removeDuplicates(self, nums: List[int]) -> int:
        left = 0
        for right in range(1, len(nums)):
            if nums[left] != nums[right]:
                left += 1
                nums[left] = nums[right]
        return left + 1
