import time                         # Mide cuánto tarda el algoritmo en ejecutarse (conteo de milisegundos).
import tracemalloc                  # Rastrea las asignaciones de memoria. Mide cuánta memoria RAM consumió el algoritmo.

from collections import deque       # Estructura de datos para agregar o quitar elementos desde ambos extremos.
                                    # Se utiliza específicamente en el algoritmo BFS (colas).

# ========================================================= Parte 2 ================================================================
# ===================================================== La construcción =============================================================

#   Inicializamos el constructor para explorar el laberinto
class Pathfinder:

    # Al crear una instancia de esta clase, recibe un objeto maze (laberinto).
    # Se asume que este objeto maze tiene las propiedades start_node, end_node y
    # un metodo get_neighbors(x, y) que conoce a qué casillas contiguas se puede mover.

    def __init__(self, maze):
        self.maze = maze

    def solve(self, algorithm_name):        # Este es el metodo principal.

        tracemalloc.start()                 # Aquí se inicia el rastreo de memoria (tracemalloc) y se guarda el tiempo exacto de inicio.

        start_time = time.perf_counter()    # Prepara el cronómetro. perf_counter es más preciso que otras funciones de tiempo.

        # Ejecuta el algoritmo elegido.
        # Ambos métodos devuelven tres cosas:

        #   1. Un booleano found (si encontró la salida).
        #   2. Una lista visited_order (el orden en que exploró las casillas)
        #   3. Un diccionario parent_map (que guarda de dónde venimos para poder trazar el camino de vuelta).

        found = False
        visited_order = []
        parent_map = {}

        if algorithm_name == "BFS":
            found, visited_order, parent_map = self._bfs()

        elif algorithm_name == "DFS":
            found, visited_order, parent_map = self._dfs()

        # Se detiene el reloj y el medidor de memoria.

        # peak_mem guarda la cantidad máxima de memoria utilizada durante la búsqueda.

        end_time = time.perf_counter()
        _, peak_mem = tracemalloc.get_traced_memory()

        tracemalloc.stop()

        # Calcula la ruta final y devuelve los resultados

        # Reconstrucción del camino:

        path = []  # Ruta explorada

        if found:                           # Si se encontró la salida (if found:)
            curr = self.maze.end_node       # Empezamos desde el nodo final (end_node)

            # Usamos el parent_map para "viajar en el tiempo" hacia atrás, paso a paso, hasta llegar al inicio.

            while curr in parent_map:

                curr = parent_map[curr]

                if curr != self.maze.start_node:
                    path.append(curr)

            # # Al final, se hace un path.reverse()
            # Porque el camino se construyó de la meta al inicio, y lo queremos del inicio a la meta.
            path.reverse()

        # Resultados
        # Devuelve un diccionario con toda la información:
        # Sí tuvo éxito, el orden de exploración, la ruta correcta, el tiempo en milisegundos y la memoria en KB (Kilobytes).

        return {
            "found": found,
            "visited_order": visited_order,
            "path": path,
            "time_ms": (end_time - start_time) * 1000,
            "peak_mem_kib": peak_mem / 1024
        }

# ========================================================= Parte 3 ================================================================
# ===================================================== Los Algoritmos =============================================================

    # Búsqueda en Anchura: _bfs (Breadth-First Search)
    # El algoritmo BFS explora el laberinto como si fuera una onda de agua en un estanque:
    # Primero revisa todos los vecinos inmediatos, luego los vecinos de los vecinos, y así sucesivamente (nivel por nivel).
    # Este algoritmo garantiza encontrar el camino más corto.

    def _bfs(self):
        queue = deque([self.maze.start_node]) # Usa una Cola (Queue):
                                              # Funciona bajo el principio FIFO, el primero en entrar es el primero en salir).
                                              # Usa deque porque popleft() extrae el elemento más antiguo de forma muy eficiente.


        # Usa un set llamado visited para no procesar el mismo nodo dos veces (y evitar ciclos infinitos).
        visited = set([self.maze.start_node])
        visited_order = []
        parent_map = {}

        # Este es el ciclo de exploración del "Árbol"

        while queue: # Si hay elementos en la cola, sigue explorando

            current = queue.popleft() # Extrae el nodo más antiguo (popleft), revisa si es la meta, y si no, busca a sus vecinos.

            if current != self.maze.start_node and current != self.maze.end_node:

                visited_order.append(current)   # Registra la exploración (sin borrar el inicio/fin)
                                                # Añade la casilla en la que estamos parados actualmente (current)
                                                # a una lista llamada visited_order (orden de visitados)
                                                # solamente si esa casilla no es el punto de partida ni la meta.

            if current == self.maze.end_node:   # Si el nodo es la meta:
                return True, visited_order, parent_map
            # devuelve encontrado, el orden de visita y el diccionario de nodos en ruta

            for nxt in self.maze.get_neighbors(current[0], current[1]): # Se asume que los nodos son tuplas de coordenadas,
                                                                        # por eso se usa current[0] (x) y current[1] (y).
                if nxt not in visited:
                    visited.add(nxt)            # Guarda al vecino en visited.
                    parent_map[nxt] = current   # Registra quién es su "padre" en parent_map.
                    queue.append(nxt)           # Lo añade al final de la cola para explorarlo más tarde.

        return False, visited_order, parent_map # Caso sin solución

    # Búsqueda en Profundidad: _dfs (Depth-First Search)
    # El algoritmo DFS explora el laberinto yendo tan profundo como sea posible por un solo camino.
    # Si choca contra una pared, retrocede (backtracking) hasta el último cruce y prueba otro camino.
    # Es más rápido para llegar a una salida si está lejos, pero no garantiza encontrar el camino más corto.

    def _dfs(self):
        stack = [self.maze.start_node]          # Usa una Pila (Stack): Funciona bajo el principio LIFO, el último en entrar es el primero en salir.
                                                # En Python, una lista normal [] funciona perfectamente como pila usando .pop().
        visited = set([self.maze.start_node])
        visited_order = []
        parent_map = {}

        # Ciclo de exploración
        while stack:    # Si la pila tiene elementos, continua buscando

            # current es la casilla en la que estamos parados en este exacto momento.

            current = stack.pop() # Saca y borra el último elemento que se metió en la lista.
                                  # Esto hace que el algoritmo salte siempre hacia la casilla más nueva descubierta,
                                  # Va a lo más profundo posible en lugar de revisar sus lados.

            if current != self.maze.start_node and current != self.maze.end_node:
            # De nuevo va añadiendo la ruta que recorre
                visited_order.append(current)

            # Si llegamos a la meta terminamos
            if current == self.maze.end_node:
                return True, visited_order, parent_map

            # Exploramos a los vecinos
            for nxt in self.maze.get_neighbors(current[0], current[1]):

                # Si no estamos en la meta, toca seguir buscando.
                # Solo nos interesan los vecinos que NO hemos visitado antes. Si ya pasamos por ahí o es una pared, lo ignoramos.
                if nxt not in visited: # (nxt/siguiente) Son los vecinos.

                    visited.add(nxt)            # Lo marcamos como "ya visto" para que nadie más vuelva a intentar procesarlo.
                    parent_map[nxt] = current   # Hacemos un rastreo paso a paso del camino que se toma.
                    stack.append(nxt)           # Metemos este nuevo vecino al final de la Pila (stack).
                                                # Como es el último en entrar, en la siguiente vuelta del while.
                                                # el pop() lo saca a primero, obligando al algoritmo a avanzar a esta nueva casilla.

        return False, visited_order, parent_map
    # Caso sin solución
