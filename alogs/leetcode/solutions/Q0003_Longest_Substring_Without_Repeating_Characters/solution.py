class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
        pass


class Solution01(Solution):
    def lengthOfLongestSubstring(self, s: str) -> int:
        # solved with two pointer
        slots = [False] * 128
        left, right, cum_max, n = 0, 0, 0, len(s)
        while right < n:
            if slots[(idx := ord(s[right]))] is False:  # if s[left] is not repeated, then move right point
                slots[idx] = True
                right += 1
            else:  # if s[left] is repeated, move left pointer until repeated character is not included
                cum_max = max(cum_max, right - left)  # before move left pointer, update the current max length
                while slots[idx] is True:
                    slots[ord(s[left])] = False
                    left += 1
        return max(cum_max, right - left)


class Solution02(Solution):
    def lengthOfLongestSubstring(self, s: str) -> int:
        # instead of using list, we use a hashmap to maintain two information:
        # 1) whether an element is duplicated in the sliding window;
        # 2) the position of each element, to reduce redundant calculation when moving left pointer;
        appearances = {}
        left, right, cum_max, n = 0, 0, 0, len(s)
        while right < n:
            # we need to test both:
            # 1) whether a character is duplicated in the hashmap;
            # 2) and its index is not out of the left bounder when left bounder is moving
            # to ensure the character is "in" the sliding window, and then process it.
            if appearances.get((char := s[right]), -1) >= left:
                cum_max = max(cum_max, right - left)
                left = appearances[char] + 1
            appearances[char] = right
            right += 1
        return max(cum_max, right - left)


if __name__ == "__main__":
    test_case = Solution02()
    test_case.lengthOfLongestSubstring(" ")
    test_case.lengthOfLongestSubstring("abba")
