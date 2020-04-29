## 2.2

### 2.2-2
`pseudocode`
```text
for i = 1 to A.length - 1:
    index = i
    key = A[index]
    for j = i + 1 to A.length:
        if A[j] < key:
            index = j
            key = A[index]
    A[index] = A[i]
    A[i] = key
```
```python
def selection_sort(arr):
    for i in range(len(arr) - 1):
        index = i
        key = arr[index]
        for j in range(i + 1, len(arr)):
            if arr[j] < key:
                index = j
                key = arr[index]
        arr[index] = arr[i]
        arr[i] = key
```