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
        self.ptr_vec, self.ptr_elem = 0, 0
        self.vectors = [v1, v2]
        self.num_vectors = len(self.vectors)

    def _move_ptr(self):
        self.ptr_vec += 1
        quo, rem = self.ptr_vec // self.num_vectors, self.ptr_vec % self.num_vectors
        self.ptr_vec, self.ptr_elem = rem, self.ptr_elem + quo

    def next(self) -> int:
        try:
            res = self.vectors[self.ptr_vec][self.ptr_elem]  # solved with two pointer
        except IndexError:
            self._move_ptr()
            return self.next()

        self._move_ptr()
        self.cur_count += 1
        return res

    def hasNext(self) -> bool:
        return self.cur_count < self.total_count
