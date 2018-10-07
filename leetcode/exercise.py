

# Q5 Longest Palindromic Substring
def longest_palindromine():
    # Manacher's algorithm
    pass


# Q9 Palindrome Number *
def is_palindrome(x):
    """
    Determine whether an integer is a palindrome. Do this without extra space.
    Some hints:
    Could negative integers be palindromes? (ie, -1)

    If you are thinking of converting the integer to string, note the restriction of using extra space.

    You could also try reversing an integer. However, if you have solved the problem "Reverse Integer", you know that the reversed integer might overflow. How would you handle such case?

    There is a more generic way of solving this problem.

    Args:
        x: integer

    Returns:
        bool
    """

    # # Method 1
    # if x < 0:
    #     return False
    #
    # l = []
    # is_palindrome = True
    #
    # while True:
    #     quotient, remainder = divmod(x, 10)
    #     l.append(remainder)
    #     x = quotient
    #     if quotient == 0:
    #         break
    #
    # L = len(l)
    # for i in range(L):
    #     lidx, ridx = i, L - i - 1
    #     if l[lidx] != l[ridx]:
    #         is_palindrome = False
    #         break
    #
    #     if ridx - lidx <= 1:
    #         break
    #
    # return is_palindrome

    # # Method 2
    if x < 0:
        return False

    if x / 10 == 0:
        return True

    if x % 10 == 0:
        return False

    h = x
    l = 0
    while h > l:
        print(f"l:{l}, h:{h}")
        l *= 10
        l += h % 10
        if l == h:
            return True
        h /= 10
    return h == l


# Q11 Container With Most Water **
def max_area(height):
    """
    Given n non-negative integers a1, a2, ..., an, where each represents a point at coordinate (i, ai). n vertical lines are drawn such that the two endpoints of line i is at (i, ai) and (i, 0). Find two lines, which together with x-axis forms a container, such that the container contains the most water.
    Note: You may not slant the container and n is at least 2.

    Args:
        height: list[int]

    Returns:
        int

    """

    points = list(enumerate(height))
    max_area = 0
    l, r = 0, len(points) - 1

    while True:
        shorter_side = l if points[l][1] <= points[r][1] else r
        area = (points[r][0] - points[l][0]) * points[shorter_side][1]
        if area > max_area:
            max_area = area

        if l == shorter_side:
            l += 1
        else:
            r -= 1

        if l == r:
            break

    return max_area


# Q26 Remove Duplicates from Sorted Array
def remove_duplicates(nums):
    """
    Given a sorted array, remove the duplicates in-place such that each element appear only once and return the new
    length.
    Do not allocate extra space for another array, you must do this by modifying the input array in-place with O(1)
    extra memory.

    Args:
        nums: list<int>

    Returns:
        int

    """

    # Method 1
    # if len(nums) == 0:
    #     return 0
    #
    # removed = 0
    #
    # for i in range(1, len(nums)):
    #     i -= removed
    #     if nums[i] == nums[i - 1]:
    #         del nums[i]  # LIST DEL operation is O(n)
    #         removed += 1
    # return len(nums)

    # Method 2
    if len(nums) == 0:
        return 0

    idx = 0
    for i in range(1, len(nums)):
        if nums[i] != nums[idx]:
            idx += 1
            nums[idx] = nums[i]

    return idx + 1


# Q53 Maximum Subarray *
def max_subarray(nums):
    """
    Find the contiguous subarray within an array (containing at least one number) which has the largest sum.

    For example, given the array [-2,1,-3,4,-1,2,1,-5,4],
    the contiguous subarray [4,-1,2,1] has the largest sum = 6.

    Args:
        nums: list[int]

    Returns:
        int

    """

    # Method 1 Kadane Algorithm
    max_so_far = max_end_here = nums[0]

    for x in nums:
        #  DP, optimal substructure:
        max_end_here = max(max_end_here + x, x)  # max_end_here[i] = max(max_end_here[i - 1] + nums[i], nums[i])
        max_so_far = max(max_so_far, max_end_here)  # max_so_far[i] = max(max_so_far[i-1], max_end_here[i])

    return max_so_far


# Q67 Add Binary *
def addBinary(a, b):
    """
    Given two binary strings, return their sum (also a binary string).
    For example,
    a = "11", b = "1"
    Return "100".

    Args:
        a: str
        b: str

    Returns:
        str

    """

    return bin(int(a, 2) + int(b, 2))[2:]


# Q100 Same Tree *
def is_same_tree(p, q):
    """
    Given two binary trees, write a function to check if they are the same or not.

    Two binary trees are considered the same if they are structurally identical and the nodes have the same value.

    Args:
        p: TreeNode
        q: TreeNode

    Returns:
        bool

    """

    # Definition for a binary tree node.
    # class TreeNode:
    #     def __init__(self, x):
    #         self.val = x
    #         self.left = None
    #         self.right = None

    if p and q:
        return p.val == q.val and is_same_tree(p.left, q.left) and is_same_tree(p.right, q.right)
    return p is q


# 112 Path Sum
class Solution:
    # Definition for a binary tree node.
    # class TreeNode:
    #     def __init__(self, x):
    #         self.val = x
    #         self.left = None
    #         self.right = None

    def hasPathSum(self, root, sum_):
        """

        Args:
            root: TreeNode
            sum_: int

        Returns:
            bool

        """

        if root is None:
            return False

        return self.walk(root, 0, sum_)

    def walk(self, node, cur, sum_):
        cur += node.val
        if cur == sum_ and node.left is None and node.right is None:
            return True

        l = r = False
        if node.left:
            l = self.walk(node.left, cur, sum_)
        if node.right:
            r = self.walk(node.right, cur, sum_)

        return l or r


# Q101 Symmetric Tree
class Solution101:
    def is_symmetric(self, root):
        """
        Given a binary tree, check whether it is a mirror of itself (ie, symmetric around its center).

        For example, this binary tree [1,2,2,3,4,4,3] is symmetric:

        Args:
            root: TreeNode

        Returns:
            bool

        """

        # Definition for a binary tree node.
        # class TreeNode:
        #     def __init__(self, x):
        #         self.val = x
        #         self.left = None
        #         self.right = None

        if root is None:
            return True
        return self.is_mirror(root.left, root.right)

    def is_mirror(self, l, r):
        if l is None and r is None:
            return True
        if (l is None) ^ (r is None):
            return False
        return l.val == r.val and self.is_mirror(l.left, r.right) and self.is_mirror(l.right, r.left)


# Q104 Maximum Depth of Binary Tree
class Solution104:
    def max_depth(self, root):
        """
        Given a binary tree, find its maximum depth.
        The maximum depth is the number of nodes along the longest path from the root node down to the farthest leaf node.
        Note: A leaf is a node with no children.

        Example:
        Given binary tree [3,9,20,null,null,15,7],
        return its depth = 3.

        Args:
            root: TreeNode

        Returns:

        """

        # Definition for a binary tree node.
        # class TreeNode:
        #     def __init__(self, x):
        #         self.val = x
        #         self.left = None
        #         self.right = None

        # Soulution 1
        if root is None:
            return 0
        return self._max_depth(root, 1)

        # Solution 2
        # if not root:
        #     return 0
        #
        # return 1 + max(self.maxDepth(root.left), self.maxDepth(root.right))

    def _max_depth(self, node, depth):
        l = r = depth
        if not node.left and not node.right:
            return depth
        else:
            if node.left:
                l = self._max_depth(node.left, depth + 1)
            if node.right:
                r = self._max_depth(node.right, depth + 1)
        return max(l, r)


# Q136 Single Number *
def single_number(nums):
    """
    Given an array of integers, every element appears twice except for one. Find that single one.

    Note:
    Your algorithm should have a linear runtime complexity. Could you implement it without using extra memory?

    Args:
        nums: list[int]

    Returns:
        int

    """

    # Method 1
    nums = sorted(nums)
    for i in range(0, len(nums) - 2, 2):
        if nums[i] != nums[i + 1]:
            return nums[i]
    return nums[-1]

    # Method 2
    # 1) N XOR N = 0
    # 2) XOR is associative & commutative
    res = 0
    for num in nums:
        res ^= num
    return res


# Q141 Linked List Cycle *
class Solution141(object):
    # Definition for singly-linked list.
    # class ListNode(object):
    #     def __init__(self, x):
    #         self.val = x
    #         self.next = None

    def has_cycle(self, head):
        """
        Given a linked list, determine if it has a cycle in it.

        Follow up:
        Can you solve it without using extra space?

        Args:
            head: ListNode

        Returns:
            bool

        """

        # METHOD 1 EAFP + Floyd's Tortoise and Hare algorithm O(n) algorithm, O(1) space
        try:
            tortoise, hare = head.next, head.next.next
            while tortoise is not hare:
                tortoise = tortoise.next
                hare = hare.next.next
            return True

        except:
            return False


# Q155 Min Stack *
class MinStack:
    """
    Design a stack that supports push, pop, top, and retrieving the minimum element in constant time.

    push(x) -- Push element x onto stack.
    pop() -- Removes the element on top of the stack.
    top() -- Get the top element.
    getMin() -- Retrieve the minimum element in the stack.

    """

    def __init__(self):
        """
        initialize your data structure here.
        """
        self.stack = []

    def push(self, x):
        """
        :type x: int
        :rtype: void
        """
        if len(self.stack) > 0:
            val = (x, min(x, self.stack[-1][1]))
            self.stack.append(val)
        self.stack.append((x, x))

    def pop(self):
        """
        :rtype: void
        """
        self.stack.pop()

    def top(self):
        """
        :rtype: int
        """
        return self.stack[-1][0]

    def getMin(self):
        """
        :rtype: int
        """
        return self.stack[-1][1]


# Q198 House Robber *
def rob(nums):
    """
    You are a professional robber planning to rob houses along a street. Each house has a certain amount of money stashed, the only constraint stopping you from robbing each of them is that adjacent houses have security system connected and it will automatically contact the police if two adjacent houses were broken into on the same night.

    Given a list of non-negative integers representing the amount of money of each house, determine the maximum amount of money you can rob tonight without alerting the police.

    Args:
        nums: list[int]

    Returns:
        int

    """

    # DP
    r = nr = 0
    for x in nums:
        r_prev = r

        r = nr + x
        nr = max(r_prev, nr)

    return max(r, nr)

    # f(0): r = nums[0]; nr = 0
    # f(1): r = nums[1]; nr = f(0)
    # f(k) = max( f(k-2) + nums[k], f(k-1) )


# Q268 Missing Number *
def missing_number(nums):
    """
    Given an array containing n distinct numbers taken from 0, 1, 2, ..., n, find the one that is missing from the
    array.

    For example,
    Given nums = [0, 1, 3] return 2.

    Note:
    Your algorithm should run in linear runtime complexity. Could you implement it using only constant extra space
    complexity?

    Credits:
    Special thanks to @jianchao.li.fighter for adding this problem and creating all test cases.

    Subscribe to see which companies asked this question

    :param nums: array containing n distinct numbers taken from 0, 1, 2, ..., n
    :return: the missing number of the array
    """

    # # Method 1 Traversal
    # nums.sort()
    # if nums[0] == 0:
    #     for i in range(len(nums) - 1):
    #         if nums[i] + 1 != nums[i + 1]:
    #             return nums[i] + 1
    #     return nums[-1] + 1
    # else:
    #     return 0

    # Method 2 Sum
    n_length = len(nums)
    return (0 + n_length - 1) * n_length / 2 - sum(nums)

    # # Method 3 XOR
    # res = len(nums)
    # for i in range(len(nums)):
    #     res ^= i
    #     res ^= nums[i]
    # return res

    # # Method 4 Binary Search
    # nums.sort()
    # length = len(nums)
    # left, right = 0, length
    # middle = (left + right) / 2
    # if nums[middle] < middle:
    #     left = middle


# Q374 Guess Number Higher or Lower *
class Solution374(object):
    # The guess API is already defined for you.
    # @param num, your guess
    # @return -1 if my number is lower, 1 if my number is higher, otherwise return 0
    # def guess(num):
    def guess(self, n):
        pass

    def guessNumber(self, n):
        """
        We are playing the Guess Game. The game is as follows:
        I pick a number from 1 to n. You have to guess which number I picked.
        Every time you guess wrong, I'll tell you whether the number is higher or lower.
        You call a pre-defined API guess(int num) which returns 3 possible results (-1, 1, or 0):

        Args:
            n: int

        Returns:
            int

        """

        lo, hi = 1, n
        while lo < hi:
            mid = (lo + hi) // 2
            res = self.guess(mid)
            if res == 1:
                lo = mid + 1
            elif res == -1:
                hi = mid
            else:
                return mid
        return lo


# Q441 Arranging Coins
class Solution441:
    def arrangeCoins(self, n):
        """
        You have a total of n coins that you want to form in a staircase shape, where every k-th row must have exactly k coins.
        Given n, find the total number of full staircase rows that can be formed.
        n is a non-negative integer and fits within the range of a 32-bit signed integer.

        n = 5

        The coins can form the following rows:
        ¤
        ¤ ¤
        ¤ ¤

        Because the 3rd row is incomplete, we return 2.

        Args:
            n: int

        Returns:
            int

        """

        return int((2 * n + 0.25) ** 0.5 - 0.5)


# Q501 Find Mode in Binary Search Tree *
class Solution501:
    """
    Given a binary search tree (BST) with duplicates, find all the mode(s) (the most frequently occurred element) in the given BST.

    Assume a BST is defined as follows:

    The left subtree of a node contains only nodes with keys less than or equal to the node's key.
    The right subtree of a node contains only nodes with keys greater than or equal to the node's key.
    Both the left and right subtrees must also be binary search trees.

    """

    # Definition for a binary tree node.
    # class TreeNode:
    #     def __init__(self, x):
    #         self.val = x
    #         self.left = None
    #         self.right = None

    def findMode(self, root):
        """
        :type root: TreeNode
        :rtype: List[int]
        """
        if root is None:
            return []

        cache = {}
        self.update_freq(root, cache)
        mode_count = max(cache.values())
        return [k for k, v in cache.items() if v == mode_count]

    def update_freq(self, node, cache):
        cache[node.val] = cache.get(node.val, 0) + 1

        if node.left:
            self.update_freq(node.left, cache)
        if node.right:
            self.update_freq(node.right, cache)


# Q643 Maximum Average Subarray I *
class Solution643:
    def findMaxAverage(self, nums, k):
        """
        Given an array consisting of n integers, find the contiguous subarray of given length k that has the maximum
        average value. And you need to output the maximum average value.
        Note:
            1 <= k <= n <= 30,000.
            Elements of the given array will be in the range [-10,000, 10,000].

        Args:
            nums: List[int]
            k: int

        Returns:
            float

        """

        current = max_total = sum(nums[:k])

        for i in range(1, len(nums) - k + 1):
            current += (nums[i + k - 1] - nums[i - 1])
            max_total = max(current, max_total)

        return max_total / k


# Q804
class Solution804:
    morses_az = [".-", "-...", "-.-.", "-..", ".", "..-.", "--.", "....", "..", ".---", "-.-", ".-..", "--", "-.", "---",
             ".--.", "--.-", ".-.", "...", "-", "..-", "...-", ".--", "-..-", "-.--", "--.."]

    def uniqueMorseRepresentations(self, words):
        """

        Args:
            words: list[str]

        Returns:
            int

        """

        return len(set(["".join([self.morses_az[ord(w) - 97] for w in word]) for word in words]))


# Q 804-1
class Solution804_1:
    morses_az = [".-", "-...", "-.-.", "-..", ".", "..-.", "--.", "....", "..", ".---", "-.-", ".-..", "--", "-.", "---", ".--.", "--.-", ".-.", "...", "-", "..-", "...-", ".--", "-..-", "-.--", "--.."]
    cnt = 0

    def another_morse_repr(self, words):
        """

        Args:
            words: str

        Returns:
            int

        """

        morses = "".join([self.morses_az[ord(w) - 97] for w in words])
        self.check_remain(morses)

        return self.cnt

    def check_remain(self, remain):
        """

        Args:
            remain: str

        Returns:

        """

        for mo in self.morses_az:
            if len(mo) < len(remain):
                if remain[:len(mo)] == mo:
                    return self.check_remain(remain[len(mo):])
            elif len(mo) == len(remain):
                if mo == remain:
                    self.cnt += 1

################################
################################

def insertion_sort(arr):
    # 1``
    for i in range(1, len(arr)):
        temp = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > temp:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = temp
    return arr

    # # 2
    # for i in range(1, len(arr)):
    #     temp = arr[i]
    #     for j in range(i, 0, -1):
    #         if arr[j - 1] > temp:
    #             arr[j] = arr[j - 1]
    #         else:
    #             j += 1
    #             break
    #     arr[j - 1] = temp
    # return arr


def merge_sorted(iter1, iter2):
    if len(iter1) > len(iter2):
        iter1, iter2 = iter2, iter1
    merged_list = []
    idx = 0
    for i in range(len(iter1)):
        for j in range(idx, len(iter2)):
            if iter1[i] < iter2[j]:
                merged_list.append(iter1[i])
                idx = j
                break
            elif iter1[i] > iter2[j]:
                merged_list.append(iter2[j])
                idx = j + 1
            else:
                merged_list.extend([iter1[i], iter2[j]])
                idx = j + 1
                break
    merged_list.extend(iter2[idx:])

    return merged_list


def mindiff(a, b):
    merged = sorted([*a, *b])
    print(merged)
    new_a, new_b = [], []
    last, count = 0, 0
    new_a.append(merged[0])
    count += 2
    for i in range(1, len(merged)):
        if last == 0 and count == 1:
            new_a.append(merged[i])
            count += 1
        elif last == 1 and count == 1:
            new_b.append(merged[i])
            count += 1
        elif last == 0 and count == 2:
            new_b.append(merged[i])
            last = 1
            count = 1
        elif last == 1 and count == 2:
            new_a.append(merged[i])
            last = 0
            count = 1

    return new_a, new_b
