def binary_search(array, v):
    le, ri = 0, len(array) - 1

    while le < ri:
        mid = (le + ri) // 2
        if v >= array[mid]:
            le = mid + 1
        else:
            ri = mid
    return le
