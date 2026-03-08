from collections import deque    # deque (Double-Ended Queue):
                                 # Permite meter y sacar datos por la izquierda o por la derecha

import time                     # Para medir el tiempo ejecución.
import tracemalloc              # Para medir cuánta memoria RAM reserva Python.


# ===================================================== Parte 1 =====================================================
# ================================================== La Estructura ==================================================

class BuscadorAlgoritmos:
    """
    Esta clase es un 'Solucionador Universal'.
    Implementa los algoritmos BFS y DFS de forma unificada para resolver un problema.
    """

    # Se inicia el constructor y recibe un objeto "problema".
    # Este objeto 'problema' tiene atributos (reglas) estado_inicial y es_objetivo.
    def __init__(self, problema):
        self.problema = problema

    def resolver(self, algoritmo):

        # Ejecuta la búsqueda y retorna tres cosas: camino_solucion, tiempo_ms, memoria_kb

        # 1. Primero evalúa si el problema tiene solución.

        if not self.problema.es_posible():
            return None, 0, 0      # Si no tiene solución, descarta de inmediato y devuelve ceros.

        # 2. Se inician los cronómetros y medidores
        tracemalloc.start()
        inicio_tiempo = time.perf_counter()

        # ============================================ Parte 2 =============================================
        # ====================================== La rutas del problema ======================================

        # 3. La 'frontera'
        # Aquí cada estado lleva su propia mochila con el historial de su viaje.

        # Guardamos una Tupla con dos elementos: (estado_actual, ruta_recorrida_hasta_aquí)
        # Si el inicio es 'A', la frontera inicia así: [('A', ['A'])]
        frontera = deque([(self.problema.estado_inicial, [self.problema.estado_inicial])])

        # 'visitados' es un conjunto que guarda los nodos visitados.
        # Evita que el algoritmo se quede atrapado caminando en círculos infinitamente.
        visitados = {self.problema.estado_inicial}

        solucion = None

        # ============================================== Parte 3 ============================================
        # ========================================== Los algoritmos =========================================

        while frontera: #Se repite mientras aún haya nodos por visitar

            # Como BFS y DFS son exactamente el mismo algoritmo, lo ÚNICO que cambia es quien
            # sale primero de la fila.

            if algoritmo == 'BFS':
                # Búsqueda en Anchura
                # Saca al MÁS ANTIGUO (popleft). Cola FIFO. Explora todos los vecinos cercanos primero.
                estado_actual, camino = frontera.popleft()

            elif algoritmo == 'DFS':
                # Búsqueda en Profundidad
                # Saca al MÁS NUEVO (pop). Pila LIFO.
                estado_actual, camino = frontera.pop()

            # Analiza si el nodo actual es la solución.
            if self.problema.es_objetivo(estado_actual):

                solucion = camino  # Devuelve la ruta de nodos
                break  # Rompemos el bucle, ya no hay que buscar más.

            # Busca cuales son los siguientes movimientos posibles.
            for sucesor in self.problema.obtener_sucesores(estado_actual):

                # Si el nodo no ha sido visitado, lo añade
                if sucesor not in visitados:
                    visitados.add(sucesor)  # Lo anotamos en la lista negra para no volver.

                    # camino + [sucesor] mo modifica la lista original.
                    # Crea una copia de la lista del viaje y le añade el nuevo paso al final.
                    # Luego mete a este nuevo estado a la sala lista de espera (frontera).
                    frontera.append((sucesor, camino + [sucesor]))

        # Finalizan los cronómetros y vemos cuánto costó la exploración.
        fin_tiempo = time.perf_counter()

        # get_traced_memory() devuelve dos valores:
        #       (memoria_actual, memoria_pico_maxima).

        # Usamos el guion bajo '_' para ignorar el primer valor porque solo nos importa el pico máximo.
        _, pico_memoria = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # El tiempo sale en segundos, multiplicamos por 1000 para tener Milisegundos (ms).
        tiempo_ms = (fin_tiempo - inicio_tiempo) * 1000

        # La memoria sale en Bytes, dividimos entre 1024 para tener Kilobytes (KB).
        memoria_kb = pico_memoria / 1024

        return solucion, tiempo_ms, memoria_kb
