import sys
import numpy as np
import pandas as pd


def main():
    li = [[1.1] * 3, [2.2] * 3]

    arr1 = np.array(li)
    arr2 = pd.DataFrame(li).values

    for arr in (arr1, arr2):
        print(f"dtype: {arr.dtype}; shape: {arr.shape}; strides: {arr.strides}; {sys.getsizeof(arr)} bytes")

    # dtype: float64; shape: (2, 3); strides: (24, 8); 160 bytes;  memory arrange in numpy
    # dtype: float64; shape: (2, 3); strides: (8, 16); 112 bytes;  memory arrange in pandas


if __name__ == '__main__':
    main()
