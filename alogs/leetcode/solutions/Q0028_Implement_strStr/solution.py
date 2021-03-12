class Solution:
    def strStr(self, haystack: str, needle: str) -> int:
        pass


class Solution01(Solution):
    def strStr(self, haystack: str, needle: str) -> int:  # brute-force
        if (len_needle := len(needle)) == 0:
            return 0

        lptr = rptr = 0

        max_index = len(haystack) - len_needle

        while lptr <= max_index:
            while rptr < len_needle:
                if haystack[lptr] != needle[rptr]:
                    break
                if rptr == len_needle - 1:
                    return lptr - len_needle + 1
                lptr += 1
                rptr += 1

            lptr -= (rptr - 1)
            rptr = 0

        return -1


if __name__ == '__main__':
    Solution01().strStr("mississippi", "issip")
