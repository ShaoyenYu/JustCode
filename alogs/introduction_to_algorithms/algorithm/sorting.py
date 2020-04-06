def insertion_sort(arr, ascending=True):
    cmp = (lambda x, y: x > y) if ascending else (lambda x, y: x < y)

    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1

        while j > -1 and cmp(arr[j], key):
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
