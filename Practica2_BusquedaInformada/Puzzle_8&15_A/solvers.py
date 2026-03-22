import heapq
import time
import tracemalloc
import numpy as np
from modelo import PuzzleModel

class AStarPuzzleSolver:
    def __init__(self, start_state, size, heuristic_type):
        self.start = np.array(start_state)
        self.size = size
        self.goal = self.generate_goal(size)
        self.h_type = heuristic_type

        # Weighted A*: Si se elige, multiplicamos la heurística para encontrar
        # la solución más rápido, aunque no sea la más corta (sub-óptima).
        self.weight = 2.0 if self.h_type == "Weighted A*" else 1.0

    def generate_goal(self, size):
        """Crea la matriz ordenada (1, 2, 3... 0) que representa la victoria."""
        goal = np.arange(1, size * size + 1).reshape(size, size)
        goal[-1, -1] = 0
        return goal

    def get_h(self, state):
        """Selecciona la función heurística según lo elegido en la interfaz."""
        if self.h_type == "Fichas fuera":
            return PuzzleModel.h_misplaced(state, self.goal)
        elif self.h_type in ["Manhattan", "Weighted A*", "Personalizada"]:
            return PuzzleModel.h_manhattan(state, self.goal)
        return 0

    def solve(self):
        # Iniciamos el rastreo de memoria y tiempo para las estadísticas de la exposición.
        tracemalloc.start()
        start_time = time.perf_counter()

        # El estado se convierte a tupla porque los arrays de NumPy no pueden ser llaves de un set.
        start_tuple = tuple(self.start.ravel())
        
        # frontera: Lista de prioridad que guarda (f, g, estado_actual, camino_recorrido)
        # f(n) = g(n) + w * h(n)
        frontier = [(self.weight * self.get_h(self.start), 0, start_tuple, [])]
        
        # visited: Diccionario para evitar ciclos (no volver a estados ya procesados).
        visited = {start_tuple: 0}
        nodes_expanded = 0
        max_nodes = 50000 if self.weight > 1.0 else 15000 # Límite para evitar colapsar la RAM.

        while frontier:
            # Extraemos el nodo con el valor 'f' más bajo (el más prometedor).
            f, g, curr_tuple, path = heapq.heappop(frontier)

            # Verificamos si llegamos a la meta.
            if curr_tuple == tuple(self.goal.ravel()):
                end_time = time.perf_counter()
                _, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                return True, path + [curr_tuple], (end_time - start_time)*1000, peak / 1024

            nodes_expanded += 1
            if nodes_expanded > max_nodes: break

            # Expandimos los sucesores: Buscamos dónde está el "0" y movemos piezas adyacentes.
            curr_state = np.array(curr_tuple).reshape(self.size, self.size)
            r, c = np.where(curr_state == 0)[0][0], np.where(curr_state == 0)[1][0]

            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]: # Arriba, Abajo, Izquierda, Derecha
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.size and 0 <= nc < self.size:
                    new_state = curr_state.copy()
                    # Intercambio de la pieza por el espacio vacío.
                    new_state[r, c], new_state[nr, nc] = new_state[nr, nc], new_state[r, c]
                    new_tuple = tuple(new_state.ravel())

                    new_g = g + 1 # El costo real aumenta en 1 paso.
                    
                    # Si el estado es nuevo o llegamos a él por un camino más corto.
                    if new_tuple not in visited or new_g < visited[new_tuple]:
                        visited[new_tuple] = new_g
                        f_new = new_g + (self.weight * self.get_h(new_state))
                        heapq.heappush(frontier, (f_new, new_g, new_tuple, path + [curr_tuple]))

        tracemalloc.stop()
        return False, [], 0, 0
