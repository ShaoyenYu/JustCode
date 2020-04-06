## 2.1

### 2.1-1
```text
<31, `41`, 59, 26, 41, 58>
<31, 41, `59`, 26, 41, 58>
<`26`, 31, 41, 59, 41, 58>
<26, 31, 41, `41`, 59, 58>
<26, 31, 41, 41, `58`, 59>
```

### 2.1-2
`pseudo`
```text
for i = 2 to A.length:
    key = A[i]
    j = i - 1
    while j > 0 and a[j] < key:
        a[j + 1] = a[j]
        j = j - 1
    a[j + 1] = key
```
`python`
```python
def insertion_sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j > -1 and arr[j] < key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
```

### 2.1-3
`pseudo`
```text
for i = 1 to A.length:
    if A[i] == v:
        return i
return NIL
```
`python`
```python
def linear_search(arr, v):
    for i in range(len(arr)):
        if arr[i] == v:
            return i
    return None
```

### 2.1-4
`pseudo`
```text
carry = 0
for i = A.length to 1:
    v = A[i] + B[i] + carry
    carry = v // 2
    v = v % 2
    C[i + 1] = v
C[0] = carry
```
`python`
```python
def binary_add(a, b):
    c = [0] * (len(a) + 1)
    carry = 0
    for i in range(len(a) - 1, -1, -1):
        v = a[i] + b[i] + carry
        carry, v = v // 2, v % 2
        c[i + 1] = v
    c[0] = carry
    return c
```