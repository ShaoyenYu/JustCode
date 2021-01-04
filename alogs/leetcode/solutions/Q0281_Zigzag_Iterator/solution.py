from typing import List

# Your ZigzagIterator object will be instantiated and called as such:
# i, v = ZigzagIterator(v1, v2), []
# while i.hasNext(): v.append(i.next())


class ZigzagIterator:
    def __init__(self, v1: List[int], v2: List[int]):
        pass

    def next(self) -> int:
        pass

    def hasNext(self) -> bool:
        pass


class ZigzagIterator01(ZigzagIterator):
    def __init__(self, v1: List[int], v2: List[int]):
        self.cur_count, self.total_count = 0, len(v1) + len(v2)
        self.ptr_vec, self.ptr_elem = 0, 0  # solved with two pointer
        self.vectors = [v1, v2]
        self.num_vectors = len(self.vectors)

    def _move_ptr(self):
        self.ptr_vec += 1
        quo, rem = self.ptr_vec // self.num_vectors, self.ptr_vec % self.num_vectors
        self.ptr_vec, self.ptr_elem = rem, self.ptr_elem + quo

    def next(self) -> int:
        try:
            res = self.vectors[self.ptr_vec][self.ptr_elem]
            self._move_ptr()
        except IndexError:
            self._move_ptr()
            return self.next()

        self.cur_count += 1
        return res

    def hasNext(self) -> bool:
        return self.cur_count < self.total_count


class ZigzagIterator02(ZigzagIterator):
    def __init__(self, v1: List[int], v2: List[int]):
        from collections import deque
        self.cur_count, self.total_count = 0, len(v1) + len(v2)
        # solved with two pointer
        # use a queue to maintain the vector pointers, to avoid redundant boundary check each time
        self.ptr_elem, self.ptrs_vec = 0, deque([0, 1])
        self.vectors = [v1, v2]
        self.pop_count, self.num_ptrs_vec = 0, len(self.ptrs_vec)

    def _move_pointer(self):
        if self.pop_count == self.num_ptrs_vec:
            self.ptr_elem += 1
            self.pop_count, self.num_ptrs_vec = 0, len(self.ptrs_vec)

    def next(self) -> int:
        ptr_vec, self.pop_count = self.ptrs_vec.popleft(), self.pop_count + 1
        try:
            res = self.vectors[ptr_vec][self.ptr_elem]
            self.ptrs_vec.append(ptr_vec)
            self._move_pointer()

        except IndexError:
            # need not add `ptr_vec` back to the pointer queue, since all elements have been iterated
            self._move_pointer()
            return self.next()

        self.cur_count += 1
        return res

    def hasNext(self) -> bool:
        return self.cur_count < self.total_count
