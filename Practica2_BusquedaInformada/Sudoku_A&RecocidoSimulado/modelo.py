import numpy as np

class SudokuBoard:
    @staticmethod
    def is_valid(board, row, col, num):
        # Verificar fila
        if num in board[row, :]: return False
        # Verificar columna
        if num in board[:, col]: return False
        # Verificar subcuadrícula 3x3
        sr, sc = 3 * (row // 3), 3 * (col // 3)
        if num in board[sr:sr+3, sc:sc+3]: return False
        return True

    @staticmethod
    def count_conflicts(board):
        conflicts = 0
        for i in range(9):
            conflicts += (9 - len(np.unique(board[i, :])))
            conflicts += (9 - len(np.unique(board[:, i])))
        return conflicts