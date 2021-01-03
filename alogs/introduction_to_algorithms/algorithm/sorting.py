def insertion_sort(array, ascending=True):
    # Pseudo Code
    # InsertionSort(A)
    # for i = 2 to A.length - 1
    #   key = A[i]
    #   while j > 0 and array[j - 1] > key
    #       array[j] = array[j - 1]
    #       j = j - 1
    #   array[j] = key

    cmp = (lambda x, y: x > y) if ascending else (lambda x, y: x < y)
    # maximums/minimums are inserted to the sorted section
    for i in range(1, len(array)):
        key = array[i]
        j = i - 1
        while j > -1 and cmp(array[j], key):
            array[j + 1] = array[j]
            j -= 1
        array[j + 1] = key


def insertion_sort(a):
    for j in range(1, len(a)):
        key = a[j]
        for i in range(j - 1, -1, -1):
            if a[i] <= key:
                i += 1
                break
            a[i + 1] = a[i]
        a[i] = key


def bubble_sort(array, ascending=True):
    # Pseudo Code
    # BubbleSort(A)
    # for i = 1 to A.length - 1
    #   for j = A.length to i + 1
    #       if A[j - 1] > A[j]
    #           exchange A[j] with A[j - 1]

    cmp = (lambda x, y: x < y) if ascending else (lambda x, y: x > y)
    # maximums/minimums are bubbled out of the unsorted section
    for i in range(len(array) - 1):
        for j in range(len(array) - 1, i, -1):
            if cmp(array[j], array[j - 1]):
                array[j], array[j - 1] = array[j - 1], array[j]


def selection_sort(array):
    # Pseudo Code
    # SelectionSort(A)
    # for i = 1 to A.length - 1:
    #   index = i
    #   key = array[index]
    #   for j = i + 1 to A.length
    #       if array[j] <= key
    #           index = j
    #           key = array[index]
    #       exchange array[i] with array[index]

    for i in range(len(array) - 1):
        index = i
        key = array[index]
        for j in range(i + 1, len(array)):
            if array[j] <= key:
                index = j
                key = array[index]
        array[index], array[i] = array[i], key


def merge_sort(array):
    def _merge(array_, p_, q_, r_):
        left = [array_[idx] for idx in range(p_, q_ + 1)]
        right = [array_[idx] for idx in range(q_ + 1, r_ + 1)]

        n1, n2 = q_ - p_ + 1, r_ - q_
        lidx, ridx = 0, 0
        k = p_
        while (lidx < n1) and (ridx < n2):
            if left[lidx] <= right[ridx]:
                array_[k] = left[lidx]
                lidx += 1
            else:
                array_[k] = right[ridx]
                ridx += 1
            k += 1

        # directly copy remain subarray to original array
        while lidx < n1:
            array_[k] = left[lidx]
            lidx += 1
            k += 1
        while ridx < n2:
            array_[k] = right[ridx]
            ridx += 1
            k += 1

    def _merge_sort(array_, p_, r_):
        if p_ < r_:
            q = (p_ + r_) >> 1
            _merge_sort(array_, p_, q)
            _merge_sort(array_, q + 1, r_)
            _merge(array_, p_, q, r_)

    p, r = 0, len(array) - 1
    _merge_sort(array, p, r)
