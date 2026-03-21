import numpy as np
import random
import math
import time
import tracemalloc
from modelo import SudokuBoard

class SudokuSolver:
    """Clase base para gestionar métricas de rendimiento."""
    def __init__(self, board):
        self.board = np.array(board)

    def get_metrics(self, func, *args):
        """Mide cuánto tiempo y memoria consume la IA al resolver."""
        tracemalloc.start()
        start_time = time.perf_counter()
        
        success, result = func(*args)
        
        end_time = time.perf_counter()
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        return {
            "success": success,
            "time": end_time - start_time,
            "memory": peak / 1024, # Convertido a KB
            "board": result
        }

class AStarSolver(SudokuSolver):
    """
    ALGORITMO DE BÚSQUEDA CON RETROCESO (BACKTRACKING):
    Es un enfoque de 'fuerza bruta inteligente' que explora el árbol de decisiones.
    """
    def solve(self):
        temp_board = self.board.copy()
        success = self._backtrack(temp_board)
        return success, temp_board

    def _backtrack(self, board):
        for r in range(9):
            for c in range(9):
                if board[r, c] == 0: # Buscamos una celda vacía
                    for num in range(1, 10):
                        if SudokuBoard.is_valid(board, r, c, num):
                            board[r, c] = num # Probamos un número
                            
                            # Recursión: Intentamos resolver el resto del tablero
                            if self._backtrack(board): return True
                            
                            # Si falla, hacemos 'Backtrack': borramos y probamos el siguiente
                            board[r, c] = 0
                    return False # Si ningún número funciona, este camino es erróneo
        return True

class SimulatedAnnealingSolver(SudokuSolver):
    """
    RECOCIDO SIMULADO (Metaheurística):
    Inspirado en cómo los metales se enfrían. Empieza aceptando errores 
    para saltar 'mínimos locales' y poco a poco se vuelve más estricto.
    """
    def solve(self, t_init=1.0, cooling=0.9995, max_iter=25000):
        current = self.board.copy()
        fixed = (current != 0) # Marcamos qué números venían de fábrica

        # Llenamos el resto con números aleatorios para empezar
        for r in range(9):
            for c in range(9):
                if not fixed[r, c]: current[r, c] = random.randint(1, 9)

        curr_c = SudokuBoard.count_conflicts(current)
        t = t_init # Temperatura inicial

        for i in range(max_iter):
            if curr_c == 0: return True, current # ¡Resuelto!
            
            # Elegimos una celda al azar que no sea fija
            r, c = random.randint(0, 8), random.randint(0, 8)
            while fixed[r, c]: r, c = random.randint(0, 8), random.randint(0, 8)

            old_val = current[r, c]
            current[r, c] = random.randint(1, 9) # Proponemos un cambio aleatorio
            new_c = SudokuBoard.count_conflicts(current)

            delta = new_c - curr_c
            # Si el cambio es mejor, lo aceptamos. 
            # Si es peor, lo aceptamos con una probabilidad basada en la Temperatura.
            if delta < 0 or random.random() < math.exp(-delta / t):
                curr_c = new_c
            else:
                current[r, c] = old_val # Rechazamos el cambio
            
            t *= cooling # Enfriamos el sistema
        
        return curr_c == 0, current
