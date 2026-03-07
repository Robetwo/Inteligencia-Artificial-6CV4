import random

# ========================================================= Parte 1 ================================================================
# =================================================== Las reglas del juego ==========================================================

#   Inicializamos el constructor para la creación del laberinto

class Maze:
    def __init__(self, size):

        # Al crear una instancia de esta clase, recibe una matriz o lista de listas size (tamaño de la cuadrícula).
        # Un metodo get_neighbors(x, y) que conoce a qué casillas contiguas se puede mover.

        # Aquí se crea un tablero cuadrado del tamaño que tenga en size.
        self.size = size

        # Todo el tablero se llena de ceros (0). Un 0 significa "camino libre" y un 1 significa "pared".
        self.grid = [[0 for _ in range(size)] for _ in range(size)]

        # Establece las coordenadas de inicio siempre en la esquina superior izquierda (0, 0)
        # y la meta en la esquina inferior derecha (size - 1, size - 1).
        self.start_node = (0, 0)
        self.end_node = (size - 1, size - 1)

    # El generador de complejidad

    def generate_random(self, complexity="low"):

        # Por defecto tiene complejidad "low" y hay un 20% de probabilidad de que cada celda sea una pared.
        # Si no, sube al 40% (0.4), haciendo un laberinto mucho más denso y difícil de navegar.

        if complexity == "low":
            wall_prob = 0.2
        else:
            wall_prob = 0.4

        # Recorre cada celda del tablero (fila por fila r, columna por columna c).
        for r in range(self.size):
            for c in range(self.size):

                # Genera un número aleatorio y lo compara con la probabilidad de una pared.
                if random.random() < wall_prob: # Decide al azar si pone una pared (1) o la deja vacía.
                    self.grid[r][c] = 1

        self._clear_start_end()
        # Limpia el inicio y la meta

    # Configuración predefinida

    def generate_predefined(self):
        # En lugar de azar, este metodo construye un pasillo con forma de "S" o serpiente.

        # Crea paredes sólidas horizontales en las filas impares (range(1, self.size, 2)).
        # Luego, usa la variable gap para abrir un solo agujero en esa pared.
        # Alterna entre el extremo derecho y el extremo izquierdo para obligar al explorador a recorrer
        # todo el ancho del tablero de ida y vuelta.

        for r in range(1, self.size, 2): # Recorre las filas (r) de la cuadrícula, pero no una por una.
                                         # Empieza en la fila 1 y avanza de 2 en 2.
            for c in range(self.size):   # A cada celda le asigna un 1.

                self.grid[r][c] = 1      # # Construye un muro de lado a lado que bloquea completamente el paso.

            # Crea aperturas intercaladas
                # 1. Toma el número de la fila actual y lo divide entre 2
                # 2. Si el residuo de dividirlo entre 2 es igual a 0.
                # Podemos diferenciar si una fila es par (residuo 0) o impar (residuo 1) en gap (brecha).

            if (r // 2) % 2 == 0:
                gap = self.size - 1
            else:
                gap = 0

            self.grid[r][gap] = 0   # Con la variable gap, vamos a esa celda en el muro que acabamos
                                    # de construir y la volvemos a convertir en un 0 (camino libre).

        self._clear_start_end()
        # Al salir de todos los bucles, se llama a esta función por seguridad.
        # Como el algoritmo pone muros a lo loco basándose en filas y columnas
        # podría poner un ladrillo justo en la entrada (0,0) o en la meta.
        # Esta función se asegura de que ambas casillas sean un 0 siempre.

    def _clear_start_end(self):
        # Garantiza que el inicio y el fin nunca sean muros
        self.grid[self.start_node[0]][self.start_node[1]] = 0
        self.grid[self.end_node[0]][self.end_node[1]] = 0

    # Esta es la función que llama la clase Pathfinder en el bucle for nxt in self.maze.get_neighbors(...).
    # Toma la posición actual (fila r, columna c) y define matemáticamente hacia dónde se puede mover:

        # Restar 1 a la fila es ir arriba.
        # Sumar 1 es ir abajo.

        # Restar 1 a la columna es ir a la izquierda.
        # Sumar 1 es ir a la derecha.

    def get_neighbors(self, r, c):

        neighbors = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
                    # Arriba, Abajo, Izquierda, Derecha

        # Calcula las coordenadas de la nueva casilla (nr, nc) y verifica dos cosas antes de decir que es un camino válido:
        # 1. No salirse del mapa.
        # 2. No chocar con paredes.

        for dr, dc in directions:
            nr, nc = r + dr, c + dc # Suma los arreglos y se interpretan los movimientos

            # Verifica que nr y nc sean mayores o iguales a 0, y menores que el tamaño total del laberinto.
            if 0 <= nr < self.size and 0 <= nc < self.size and self.grid[nr][nc] == 0:

                # Lo añade a la lista de neighbors (vecinos) y se la devuelve al algoritmo de búsqueda.

                neighbors.append((nr, nc))

        return neighbors
