import numpy as np  # Importamos NumPy para realizar operaciones vectoriales de alta velocidad

class CustomKNN:
    # Constructor: Inicializa el número de vecinos (K) y la métrica de distancia seleccionada
    def __init__(self, k=5, metric="Euclidiana (L2)"):
        self.k = k  # Cantidad de vecinos más cercanos a considerar para la votación
        self.metric = metric  # Nombre de la métrica matemática activa
        self.X_train = None  # Almacén para los atributos geométricos de entrenamiento
        self.y_train = None  # Almacén para las etiquetas de clase de entrenamiento

    # Función privada para calcular la distancia geométrica entre dos vectores (instancias)
    def _calcular_distancia(self, x1, x2):
        if self.metric == "Euclidiana (L2)":
            # Fórmula L2: Raíz cuadrada de la suma de las diferencias al cuadrado
            return np.sqrt(np.sum((x1 - x2) ** 2))
            
        elif self.metric == "Manhattan (L1)":
            # Fórmula L1: Suma de las diferencias absolutas (distancia en cuadrícula)
            return np.sum(np.abs(x1 - x2))
            
        elif self.metric == "Chebyshev (Linf)":
            # Fórmula L-infinito: Obtiene únicamente la diferencia máxima entre todas las dimensiones
            return np.max(np.abs(x1 - x2))
            
        elif self.metric == "Camberra (No-Minkowski)":
            # Métrica fuera de Minkowski: Suma ponderada de las diferencias absolutas sobre la suma de magnitudes
            denominador = np.abs(x1) + np.abs(x2)
            denominador[denominador == 0] = 1e-8  # Parche de seguridad para evitar divisiones indeterminadas por cero
            return np.sum(np.abs(x1 - x2) / denominador)
            
        # Retorno por defecto si no coincide el nombre (Euclidiana)
        return np.sqrt(np.sum((x1 - x2) ** 2))

    # El "entrenamiento" en KNN: Al ser un clasificador perezoso, solo guarda los datos en memoria
    def fit(self, X_train, y_train):
        self.X_train = np.array(X_train, dtype=float)  # Convertimos los atributos a matrices numéricas puras
        self.y_train = np.array(y_train, dtype=int)    # Convertimos las etiquetas de clase a enteros

    # Función de predicción: Recibe una matriz de prueba y calcula su clase correspondiente
    def predict(self, X_test):
        X_test = np.array(X_test, dtype=float)  # Forzamos que los datos de entrada sean flotantes
        predicciones = []  # Lista donde guardaremos el veredicto de cada muestra
        
        # Iteramos renglón por renglón sobre el conjunto de prueba
        for x_test in X_test:
            # Calculamos la distancia desde el punto actual a ABSOLUTAMENTE TODOS los puntos de entrenamiento
            distancias = [self._calcular_distancia(x_test, x_train) for x_train in self.X_train]
            
            # Ordenamos las distancias de menor a mayor y tomamos los índices de los primeros K vecinos
            k_indices = np.argsort(distancias)[:self.k]
            
            # Extraemos las etiquetas de clase de esos K vecinos seleccionados
            k_etiquetas = self.y_train[k_indices]
            
            # np.bincount cuenta cuántas veces se repite cada clase entre los vecinos (voto mayoritario)
            votos = np.bincount(k_etiquetas)
            
            # np.argmax se queda con el número de clase que obtuvo la mayor cantidad de votos
            predicciones.append(np.argmax(votos))
            
        return np.array(predicciones)  # Retornamos la lista de predicciones como un vector numérico

# Función global auxiliar para calcular el porcentaje de aciertos
def calcular_accuracy(y_true, y_pred):
    # Suma todas las coincidencias exactas y las divide entre el número total de muestras
    return np.sum(y_true == y_pred) / len(y_true)
