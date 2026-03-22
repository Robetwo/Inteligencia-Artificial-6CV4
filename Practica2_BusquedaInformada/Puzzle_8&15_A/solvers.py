import heapq                    # Librería para manejar una "Cola de Prioridad" (saca siempre el menor costo f)
import time                     # Para medir cuántos milisegundos tarda la IA en pensar
import tracemalloc              # Para medir cuánta memoria RAM consume el algoritmo
import numpy as np              # Para manipular el tablero como una matriz (facilita encontrar el '0')
from modelo import PuzzleModel  # Importa las funciones h(n) (Manhattan, etc.) de otro archivo

# Inicializa el buscador con el estado actual del puzzle
class AStarPuzzleSolver:

    def __init__(self, start_state, size, heuristic_type):

        self.start = np.array(start_state)      # El tablero desordenado que recibe de la interfaz
        self.size = size                        # 3 o 4 (tamaño de la cuadrícula)
        self.goal = self.generate_goal(size)    # Crea automáticamente la matriz "Meta" (1,2,3...0)
        self.h_type = heuristic_type            # El nombre de la estrategia elegida (ej: "Manhattan")

        # --- WEIGHTED A* ---
        # Si eliges esta opción, la IA se vuelve "agresiva". Multiplica la importancia
        # de la heurística por 2. Encuentra la solución MUCHO más rápido, pero
        # a veces da pasos de más (no garantiza el camino más corto).
        self.weight = 2.0 if self.h_type == "Weighted A*" else 1.0

    # Crea la matriz ordenada (1, 2, 3... 0) que representa la victoria.
    def generate_goal(self, size):

        # np.arange crea [1, 2, 3...], reshape lo hace cuadrado
        goal = np.arange(1, size * size + 1).reshape(size, size)
        goal[-1, -1] = 0  # El último número (ej: 9 o 16) se reemplaza por el espacio vacío (0)

        return goal

    # Consulta al archivo 'modelo.py' para obtener el valor h(n)
    def get_h(self, state):

        if self.h_type == "Fichas fuera":
            return PuzzleModel.h_misplaced(state, self.goal)  # Cuenta cuántas piezas no están en su sitio

        elif self.h_type in ["Manhattan", "Weighted A*", "Personalizada"]:

            # Calcula la distancia total que cada pieza debe viajar hasta su meta
            return PuzzleModel.h_manhattan(state, self.goal)

        return 0

    # Función principal que ejecuta el algoritmo A*
    def solve(self):

        # Iniciamos el rastreo de recursos del sistema
        tracemalloc.start()
        start_time = time.perf_counter()

        # Convertimos la matriz a tupla plana. ¿Por qué? Porque las listas de Python
        # y los arrays de NumPy no pueden ser llaves de un diccionario (son mutables).
        # Ejemplo: [[1,2],[3,0]] -> (1, 2, 3, 0)
        start_tuple = tuple(self.start.ravel())

        # --- LA FRONTERA (LISTA ABIERTA) ---
        # Es una lista que heapq mantiene ordenada de menor a mayor costo f.
        # Estructura: (costo_f, costo_g, estado, camino_recorrido)
        # f = g + (w * h)
        frontier = [(self.weight * self.get_h(self.start), 0, start_tuple, [])]

        # --- DICCIONARIO VISITED (LISTA CERRADA) ---
        # Guarda estados que ya vimos para no entrar en bucles infinitos.
        # También guarda el costo 'g' más bajo para llegar a ese estado.
        visited = {start_tuple: 0}

        nodes_expanded = 0  # Contador para saber cuántos tableros ha analizado la IA

        # Límite de seguridad para que la PC no se congele si el puzzle es muy difícil
        max_nodes = 50000 if self.weight > 1.0 else 15000

        while frontier:

            # heapq.heappop saca el nodo con el 'f' más bajito (el que parece mejor opción)
            f, g, curr_tuple, path = heapq.heappop(frontier)

            # --- VERIFICACIÓN DE VICTORIA ---
            if curr_tuple == tuple(self.goal.ravel()):

                end_time = time.perf_counter()              # Detiene el cronómetro
                _, peak = tracemalloc.get_traced_memory()   # Obtiene el punto máximo de uso de RAM
                tracemalloc.stop()

                # Retorna: Éxito, El camino de pasos, Tiempo en ms, Memoria en KB
                return True, path + [curr_tuple], (end_time - start_time) * 1000, peak / 1024

            # Si ya buscamos demasiado y no encontramos nada, nos detenemos
            nodes_expanded += 1

            if nodes_expanded > max_nodes: break

            # --- EXPANSIÓN DE SUCESORES ---

            # Reconvertimos la tupla en matriz para localizar el espacio vacío (el 0)
            curr_state = np.array(curr_tuple).reshape(self.size, self.size)

            # Encuentra las coordenadas (r = fila, c = columna) donde está el 0
            r, c = np.where(curr_state == 0)[0][0], np.where(curr_state == 0)[1][0]

            # Intenta mover el vacío en las 4 direcciones posibles
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:

                nr, nc = r + dr, c + dc  # Nueva posición del vacío

                # Si el movimiento es válido (no se sale de la caja 3x3 o 4x4)
                if 0 <= nr < self.size and 0 <= nc < self.size:

                    new_state = curr_state.copy()

                    # Intercambiamos el número por el espacio vacío (el movimiento del puzzle)
                    new_state[r, c], new_state[nr, nc] = new_state[nr, nc], new_state[r, c]
                    new_tuple = tuple(new_state.ravel())

                    # El costo 'g' (pasos dados) aumenta en 1
                    new_g = g + 1

                    # --- REGLA DE EXPLORACIÓN ---
                    # Si nunca habíamos visto este estado, o si llegamos a él
                    # con menos pasos que antes (un camino más corto):
                    if new_tuple not in visited or new_g < visited[new_tuple]:

                        visited[new_tuple] = new_g  # Marcamos como visitado/actualizado

                        # Calculamos el nuevo costo total f(n) = g(n) + h(n)
                        f_new = new_g + (self.weight * self.get_h(new_state))

                        # Lo metemos a la frontera para que la IA lo analice luego
                        # Guardamos el camino ('path') añadiendo el estado actual
                        heapq.heappush(frontier, (f_new, new_g, new_tuple, path + [curr_tuple]))

        # Si sale del bucle 'while' sin encontrar la meta, es que falló
        tracemalloc.stop()

        return False, [], 0, 0