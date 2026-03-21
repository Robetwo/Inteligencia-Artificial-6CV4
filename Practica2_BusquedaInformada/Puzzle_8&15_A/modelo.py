import numpy as np

class PuzzleModel:
    @staticmethod
    def get_pos(val, goal):
        """Busca las coordenadas (fila, columna) de un valor en la matriz meta."""
        res = np.where(goal == val)
        return res[0][0], res[1][0]

    @staticmethod
    def h_misplaced(state, goal):
        """
        Heurística de Fichas Fuera de Lugar:
        Cuenta cuántas piezas no están en su posición correcta.
        Es una estimación simple pero menos precisa que Manhattan.
        """
        return np.sum((state != goal) & (state != 0))

    @staticmethod
    def h_manhattan(state, goal):
        """
        Heurística de Distancia Manhattan:
        Calcula la suma de las distancias horizontales y verticales que cada ficha 
        debe recorrer para llegar a su posición objetivo.
        Es mucho más eficiente para guiar al algoritmo A*.
        """
        dist = 0
        for i in range(state.shape[0]):
            for j in range(state.shape[1]):
                val = state[i, j]
                if val != 0:
                    gr, gc = PuzzleModel.get_pos(val, goal)
                    dist += abs(i - gr) + abs(j - gc)
        return dist
