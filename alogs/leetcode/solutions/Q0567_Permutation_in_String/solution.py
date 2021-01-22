class Solution:
    def checkInclusion(self, s1: str, s2: str) -> bool:
        pass


class Solution01(Solution):
    def checkInclusion(self, s1: str, s2: str) -> bool:
        left, right, count, max_count, counts = 0, 0, len(s1), len(s2), {}
        for char in s1:
            counts[char] = counts.get(char, 0) + 1

        while right < max_count:
            char = s2[right]
            if char in counts:
                if counts[char] > 0:
                    counts[char], count = counts[char] - 1, count - 1
                    right += 1

                    if count == 0:
                        return True
                else:
                    while counts[char] == 0:
                        if (char_left := s2[left]) in counts:
                            counts[char_left], count = counts[char_left] + 1, count + 1
                        left += 1
            else:
                right += 1
                while left < right:
                    if (char_left := s2[left]) in counts:
                        counts[char_left], count = counts[char_left] + 1, count + 1
                    left += 1
        return False
