from collections import deque
import time
import tracemalloc

class BuscadorAlgoritmos:
    """Implementa los algoritmos BFS y DFS de forma unificada."""

    def __init__(self, problema):
        self.problema = problema

    def resolver(self, algoritmo):
        """
        Ejecuta la búsqueda y retorna: (camino_solucion, tiempo_ms, memoria_kb)
        """
        # Cláusula de guarda: Si el problema no tiene solución matemática, abortamos.
        if hasattr(self.problema, 'es_posible') and not self.problema.es_posible():
            return None, 0, 0

        tracemalloc.start()
        inicio_tiempo = time.perf_counter()

        # La frontera guarda tuplas: (estado_actual, historial_de_ruta)
        frontera = deque([(self.problema.estado_inicial, [self.problema.estado_inicial])])
        visitados = {self.problema.estado_inicial}
        solucion = None

        while frontera:
            # Unificación: Extraemos del principio (Cola/BFS) o del final (Pila/DFS)
            if algoritmo == 'BFS':
                estado_actual, camino = frontera.popleft() 
            elif algoritmo == 'DFS':
                estado_actual, camino = frontera.pop()     

            # ¿Llegamos a la meta?
            if self.problema.es_objetivo(estado_actual):
                solucion = camino
                break

            # Exploramos los movimientos válidos desde donde estamos
            for sucesor in self.problema.obtener_sucesores(estado_actual):
                if sucesor not in visitados:
                    visitados.add(sucesor)
                    # Creamos una nueva mochila con la historia + el nuevo paso
                    frontera.append((sucesor, camino + [sucesor]))

        # Cálculos de rendimiento
        fin_tiempo = time.perf_counter()
        _, pico_memoria = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        tiempo_ms = (fin_tiempo - inicio_tiempo) * 1000
        memoria_kb = pico_memoria / 1024

        return solucion, tiempo_ms, memoria_kb
