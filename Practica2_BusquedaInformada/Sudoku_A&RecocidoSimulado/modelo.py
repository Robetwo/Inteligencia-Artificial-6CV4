import numpy as np

class SudokuBoard:
    @staticmethod
    def is_valid(board, row, col, num):
        """
        REGLA DE ORO DEL SUDOKU:
        Verifica si un número puede ser colocado en una posición específica.
        """
        # 1. Verificar fila: El número no debe repetirse en la misma línea horizontal.
        if num in board[row, :]: return False
        
        # 2. Verificar columna: El número no debe repetirse en la misma línea vertical.
        if num in board[:, col]: return False
        
        # 3. Verificar subcuadrícula 3x3: El número no debe estar en su cuadro local.
        sr, sc = 3 * (row // 3), 3 * (col // 3)
        if num in board[sr:sr+3, sc:sc+3]: return False
        
        return True # Si pasa todas las pruebas, el movimiento es válido.

    @staticmethod
    def count_conflicts(board):
        """
        FUNCIÓN DE COSTO (Para Recocido Simulado):
        Cuenta cuántos números faltan para que cada fila y columna sea perfecta.
        Un Sudoku resuelto tiene 0 conflictos.
        """
        conflicts = 0
        for i in range(9):
            # Comparamos el tamaño total (9) contra los números únicos presentes.
            conflicts += (9 - len(np.unique(board[i, :])))
            conflicts += (9 - len(np.unique(board[:, i])))
        return conflicts
