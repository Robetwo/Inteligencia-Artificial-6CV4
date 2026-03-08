import random

class ProblemaPuzzle8:

    # --- 1. CONSTRUCTOR ---
    def __init__(self, estado_inicial):
        # Convertimos la lista de entrada en una TUPLA.

        self.estado_inicial = tuple(estado_inicial)

        # El estado de meta: Los números ordenados y el 0 (hueco) al final.
        self.objetivo = (1, 2, 3, 4, 5, 6, 7, 8, 0)

    # --- 2. CONDICIÓN DE META ---
    def es_objetivo(self, estado):
        # Retorna True si el estado actual es igual a la meta.
        return estado == self.objetivo

    # --- 3. FILTRO DE POSIBILIDAD ---
    def es_posible(self):
        # Llama a la función que verifica si el tablero inicial tiene solución.
        return self.validar_inversiones(self.estado_inicial)

    @staticmethod

    def validar_inversiones(estado):
        """Calcula si un estado tiene solución matemática."""
        inversiones = 0

        # Filtramos el 0. Para calcular las inversiones, imaginamos el tablero
        # como una línea recta sin contar el espacio vacío.
        fichas = [n for n in estado if n != 0]

        # Un bucle anidado para comparar cada ficha con todas las que están a su derecha.
        for i in range(len(fichas)):
            for j in range(i + 1, len(fichas)):
                # Una "inversión" ocurre cuando un número mayor está ANTES que un número menor.
                # Ejemplo: En la secuencia [2, 1, 3], el 2 está antes que el 1. Eso es 1 inversión.
                if fichas[i] > fichas[j]:
                    inversiones += 1

        # Si la cuadrícula es de ancho impar (3x3), el puzzle solo tiene solución
        # si el número total de inversiones es PAR (residuo de dividir entre 2 es 0).
        return inversiones % 2 == 0

    @staticmethod
    def generar_aleatorio():
        """Genera un tablero aleatorio y garantiza que tenga solución."""
        # Crea una lista ordenada del 0 al 8: [0, 1, 2, 3, 4, 5, 6, 7, 8]
        estado = list(range(9))

        while True:
            random.shuffle(estado)  # Desordena la lista al azar

            # Solo si la mezcla aleatoria resulta ser resoluble (inversiones pares),
            # rompemos el bucle y la devolvemos como tupla.
            if ProblemaPuzzle8.validar_inversiones(estado):
                return tuple(estado)

    # --- 6. EL ÁRBOL DE DECISIONES (Transiciones) ---

    def obtener_sucesores(self, estado):
        sucesores = []

        # Buscamos en qué posición exacta (del 0 al 8) está escondido el hueco (0).
        idx_hueco = estado.index(0)

        # TRUCO GENIAL DE PYTHON: divmod() hace una división y te da el cociente y el residuo a la vez.
        # Al dividir el índice 1D entre 3 (ancho del tablero):
        # - El cociente es la FILA.
        # - El residuo es la COLUMNA.
        # Ejemplo: Si idx_hueco es 5 -> 5 // 3 = Fila 1 | 5 % 3 = Columna 2.
        fila, col = divmod(idx_hueco, 3)

        # Coordenadas relativas (Fila, Columna) para moverse:
        # Arriba (-1, 0), Abajo (1, 0), Izquierda (0, -1), Derecha (0, 1)
        movimientos = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for df, dc in movimientos:
            # Calculamos la coordenada 2D de la ficha que queremos deslizar hacia el hueco
            nueva_fila, nueva_col = fila + df, col + dc

            # Comprobación de colisiones: Evitamos salirnos del tablero de 3x3
            if 0 <= nueva_fila < 3 and 0 <= nueva_col < 3:
                # Deshacemos el truco: Convertimos la coordenada 2D de vuelta a índice 1D
                # Fórmula: (fila * ancho) + columna
                nuevo_idx = nueva_fila * 3 + nueva_col

                # Las tuplas no se pueden modificar, así que hacemos una copia temporal en forma de Lista
                nuevo_estado = list(estado)

                # INTERCAMBIO (Swap): Ponemos la ficha en el lugar del hueco, y el hueco en el lugar de la ficha
                nuevo_estado[idx_hueco], nuevo_estado[nuevo_idx] = nuevo_estado[nuevo_idx], nuevo_estado[idx_hueco]

                # Volvemos a congelar la lista en tupla y la agregamos a los futuros posibles
                sucesores.append(tuple(nuevo_estado))

        # Entregamos la lista con (hasta 4) tableros nuevos posibles
        return sucesores
