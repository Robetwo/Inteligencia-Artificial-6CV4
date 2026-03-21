import numpy as np
import random
import math
import time
import tracemalloc
from modelo import SudokuBoard


class SudokuSolver:
    def __init__(self, board):
        self.board = np.array(board)

    def get_metrics(self, func, *args):
        tracemalloc.start()
        start_time = time.perf_counter()
        success, result = func(*args)
        end_time = time.perf_counter()
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        return {
            "success": success,
            "time": end_time - start_time,
            "memory": peak / 1024,
            "board": result
        }


class AStarSolver(SudokuSolver):
    def solve(self):
        temp_board = self.board.copy()
        success = self._backtrack(temp_board)
        return success, temp_board

    def _backtrack(self, board):
        for r in range(9):
            for c in range(9):
                if board[r, c] == 0:
                    for num in range(1, 10):
                        if SudokuBoard.is_valid(board, r, c, num):
                            board[r, c] = num
                            if self._backtrack(board): return True
                            board[r, c] = 0
                    return False
        return True


class SimulatedAnnealingSolver(SudokuSolver):
    def solve(self, t_init=1.0, cooling=0.9995, max_iter=25000):
        current = self.board.copy()
        fixed = (current != 0)

        for r in range(9):
            for c in range(9):
                if not fixed[r, c]: current[r, c] = random.randint(1, 9)

        curr_c = SudokuBoard.count_conflicts(current)
        t = t_init

        for i in range(max_iter):
            if curr_c == 0: return True, current
            r, c = random.randint(0, 8), random.randint(0, 8)
            while fixed[r, c]: r, c = random.randint(0, 8), random.randint(0, 8)

            old_val = current[r, c]
            current[r, c] = random.randint(1, 9)
            new_c = SudokuBoard.count_conflicts(current)

            delta = new_c - curr_c
            if delta < 0 or random.random() < math.exp(-delta / t):
                curr_c = new_c
            else:
                current[r, c] = old_val
            t *= cooling

        return curr_c == 0, current