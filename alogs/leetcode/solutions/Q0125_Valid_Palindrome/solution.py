class Solution:
    def isPalindrome(self, s: str) -> bool:
        pass


class Solution01(Solution):
    def isPalindrome(self, s: str) -> bool:
        lptr, rptr = 0, len(s) - 1
        while lptr < rptr:
            if not (left := s[lptr].lower()).isalnum():
                lptr += 1
                continue
            if not (right := s[rptr].lower()).isalnum():
                rptr -= 1
                continue

            if not left == right:
                return False

            lptr += 1
            rptr -= 1

        return True
