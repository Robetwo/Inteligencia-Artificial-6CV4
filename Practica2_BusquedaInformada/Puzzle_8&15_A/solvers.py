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

        # --- LÓGICA DE HEURÍSTICA PERSONALIZADA ---
        # Si eligen "Personalizada", usamos un peso de 2.0 (Weighted A*)
        # Si eligen otra, usamos peso 1.0 (A* Estándar)
        self.weight = 2.0 if self.h_type == "Personalizada" else 1.0

    def generate_goal(self, size):
        goal = np.arange(1, size * size + 1).reshape(size, size)
        goal[-1, -1] = 0
        return goal

    def get_h(self, state):
        # La Heurística Personalizada se basa en Manhattan pero será multiplicada por el peso
        if self.h_type == "Fichas fuera":
            return PuzzleModel.h_misplaced(state, self.goal)
        elif self.h_type == "Manhattan" or self.h_type == "Personalizada":
            return PuzzleModel.h_manhattan(state, self.goal)
        return 0

    def solve(self):
        tracemalloc.start()
        start_time = time.perf_counter()

        start_tuple = tuple(self.start.ravel())
        # Aplicamos el peso desde el cálculo del primer nodo
        frontier = [(self.weight * self.get_h(self.start), 0, start_tuple, [])]
        visited = {start_tuple: 0}

        nodes_expanded = 0
        max_nodes = 50000 if self.weight > 1.0 else 15000

        while frontier:
            f, g, curr_tuple, path = heapq.heappop(frontier)

            if curr_tuple == tuple(self.goal.ravel()):
                end_time = time.perf_counter()
                _, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                return True, path + [curr_tuple], (end_time - start_time)*1000, peak / 1024

            nodes_expanded += 1
            if nodes_expanded > max_nodes: break

            curr_state = np.array(curr_tuple).reshape(self.size, self.size)
            r, c = np.where(curr_state == 0)[0][0], np.where(curr_state == 0)[1][0]

            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.size and 0 <= nc < self.size:
                    new_state = curr_state.copy()
                    new_state[r, c], new_state[nr, nc] = new_state[nr, nc], new_state[r, c]
                    new_tuple = tuple(new_state.ravel())

                    new_g = g + 1
                    if new_tuple not in visited or new_g < visited[new_tuple]:
                        visited[new_tuple] = new_g
                        # F(n) = g(n) + W * h(n)
                        f_new = new_g + (self.weight * self.get_h(new_state))
                        heapq.heappush(frontier, (f_new, new_g, new_tuple, path + [curr_tuple]))

        tracemalloc.stop()
        return False, [], 0, 0