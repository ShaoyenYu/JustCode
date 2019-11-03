class Point:
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __iter__(self):
        return iter((self.x, self.y))


class Rect:
    __slots__ = ("left", "top", "right", "bottom", "width", "height", "center")

    def __init__(self, left=None, top=None, right=None, bottom=None, left_up=None, right_bottom=None):
        if left_up:
            self.left, self.top = left_up
        else:
            self.left = left
            self.top = top
        if right_bottom:
            self.right, self.bottom = right_bottom
        else:
            self.right = right
            self.bottom = bottom

        self.width = self.right - self.left
        self.height = self.bottom - self.top
        self.center = Point(self.left + self.width // 2, self.top + self.height // 2)

    def __iter__(self):
        return iter((self.left, self.top, self.right, self.bottom))

    def __repr__(self):
        return f"{self.left, self.top, self.right, self.bottom}"
