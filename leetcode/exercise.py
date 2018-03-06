# Q9 Palindrome Number *
def isPalindrome(x):
    """
    Determine whether an integer is a palindrome. Do this without extra space.
    Some hints:
    Could negative integers be palindromes? (ie, -1)

    If you are thinking of converting the integer to string, note the restriction of using extra space.

    You could also try reversing an integer. However, if you have solved the problem "Reverse Integer", you know that the reversed integer might overflow. How would you handle such case?

    There is a more generic way of solving this problem.

    Args:
        x:

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
