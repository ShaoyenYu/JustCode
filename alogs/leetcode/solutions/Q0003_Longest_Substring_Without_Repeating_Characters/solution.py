class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
        pass


class Solution01(Solution):
    def lengthOfLongestSubstring(self, s: str) -> int:
        # solved with two pointer
        slots = [False] * 128
        left, right, cum_max = 0, 0, 0
        while right < len(s):
            if slots[(idx := ord(s[right]))] is False:  # if s[left] is not repeated, then move right point
                slots[idx] = True
                right += 1
            else:  # if s[left] is repeated, move left pointer until repeated character is not included
                cum_max = max(cum_max, right - left)  # before move left pointer, update the current max length
                while slots[idx] is True:
                    slots[ord(s[left])] = False
                    left += 1
        return max(cum_max, right - left)
