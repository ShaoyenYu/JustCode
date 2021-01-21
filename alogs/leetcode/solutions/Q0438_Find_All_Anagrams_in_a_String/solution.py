from typing import List


class Solution:
    def findAnagrams(self, s: str, p: str) -> List[int]:
        pass


class Solution01(Solution):
    def findAnagrams(self, s: str, p: str) -> List[int]:
        left, right, count, counts = 0, 0, len(p), {}
        results = []
        for char in p:
            counts[char] = counts.get(char, 0) + 1

        while right < len(s):
            char = s[right]

            if char in counts:
                if counts[char] > 0:
                    counts[char] -= 1
                    count -= 1
                    right += 1

                    if count == 0:
                        results.append(left)

                else:
                    while counts[char] == 0:
                        if s[left] in counts:
                            counts[s[left]] += 1
                            count += 1
                        left += 1
            else:
                right += 1
                while left < right:
                    if s[left] in counts:
                        counts[s[left]] += 1
                        count += 1
                    left += 1

        return results


if __name__ == '__main__':
    s = Solution01()

    s.findAnagrams("cbaebabacd", "abc")
    s.findAnagrams("baa", "aa")
    s.findAnagrams("", "")
