

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
