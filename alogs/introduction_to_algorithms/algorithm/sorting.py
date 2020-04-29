def insertion_sort(array, ascending=True):
    cmp = (lambda x, y: x > y) if ascending else (lambda x, y: x < y)

    for i in range(1, len(array)):
        key = array[i]
        j = i - 1

        while j > -1 and cmp(array[j], key):
            array[j + 1] = array[j]
            j -= 1
        array[j + 1] = key


def selection_sort(array):
    for i in range(len(array) - 1):
        index = i
        key = array[index]
        for j in range(i + 1, len(array)):
            if array[j] <= key:
                index = j
                key = array[index]
        array[index], array[i] = array[i], key


def merge_sort(array):
    def _merge(array, p, q, r):
        left = [array[idx] for idx in range(p, q + 1)]
        right = [array[idx] for idx in range(q + 1, r + 1)]

        n1, n2 = q - p + 1, r - q
        lidx, ridx = 0, 0
        k = p
        while (lidx < n1) and (ridx < n2):
            if left[lidx] <= right[ridx]:
                array[k] = left[lidx]
                lidx += 1
            else:
                array[k] = right[ridx]
                ridx += 1
            k += 1

        # directly copy remain subarray to original array
        while lidx < n1:
            array[k] = left[lidx]
            lidx += 1
            k += 1
        while ridx < n2:
            array[k] = right[ridx]
            ridx += 1
            k += 1

    def _merge_sort(array, p, r):
        if p < r:
            q = (p + r) >> 1
            _merge_sort(array, p, q)
            _merge_sort(array, q + 1, r)
            _merge(array, p, q, r)

    p, r = 0, len(array) - 1
    _merge_sort(array, p, r)
