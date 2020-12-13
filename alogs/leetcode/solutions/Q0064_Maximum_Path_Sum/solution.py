from typing import List


class Solution:
    def minPathSum(self, x: int) -> bool:
        pass


class Solution01(Solution):
    def minPathSum(self, grid: List[List[int]]) -> int:
        if len(grid) == 0 or len(grid[0]) == 0:
            return 0
        for j in range(1, len(grid[0])):
            grid[0][j] = grid[0][j - 1] + grid[0][j]
        for i in range(1, len(grid)):
            grid[i][0] = grid[i - 1][0] + grid[i][0]
        for j in range(1, len(grid[0])):
            for i in range(1, len(grid)):
                grid[i][j] = grid[i][j] + min(grid[i - 1][j], grid[i][j - 1])
        return grid[-1][-1]
