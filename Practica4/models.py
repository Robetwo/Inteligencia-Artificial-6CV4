import pandas as pd  # Usado para manipular los marcos de datos (DataFrames) de los archivos CSV
import numpy as np   # Usado para las particiones aleatorias y segmentaciones matriciales
from algorithms import calcular_accuracy  # Importamos la métrica de éxito del archivo anterior

class DataModel:
    # Constructor: Inicializa las variables que guardarán los estados de los datos y el EDA
    def __init__(self):
        self.df = None          # Contenedor del DataFrame crudo de Pandas
        self.X = None           # Matriz de variables independientes (atributos numéricos)
        self.y = None           # Vector de la variable dependiente (etiquetas objetivo)
        self.info_eda = {}      # Diccionario para almacenar las estadísticas del análisis exploratorio

    # Función principal de carga y limpieza de datos
    def cargar_y_limpiar_dataset(self, ruta_csv):
        self.df = pd.read_csv(ruta_csv)  # Lectura del archivo físico mediante Pandas
        
        # Almacenamos el volumen real de renglones del archivo original para mostrar en el banner superior
        filas_totales_original = self.df.shape[0]
        
        # --- 🧠 ALGORITMO DE SELECCIÓN DE TARGET UNIVERSAL ---
        columna_actual_target = self.df.columns[-1]  # Revisamos la última columna de la derecha
        valores_unicos_actual = len(self.df[columna_actual_target].unique())  # Contamos cuántas clases variantes tiene
        
        # Si la última columna tiene más de 15 valores únicos, asumimos que es una tarea de regresión (como price)
        if valores_unicos_actual > 15:
            mejor_columna = None
            # Buscamos en todo el archivo alguna columna categórica/texto que tenga entre 2 y 15 valores discretos
            for col in self.df.columns:
                if self.df[col].dtype == 'object' or hasattr(self.df[col], 'cat'):
                    if 2 <= len(self.df[col].unique()) <= 15:
                        mejor_columna = col
                        break
            # Si no hay texto, buscamos una columna numérica entera que sirva de clase (como quality de vinos)
            if not mejor_columna:
                for col in self.df.columns:
                    if 2 <= len(self.df[col].unique()) <= 15:
                        mejor_columna = col
                        break
            # Si encontramos una mejor columna, reordenamos el DataFrame para mandarla al final de la derecha
            if mejor_columna:
                columnas_reordenadas = [col for col in self.df.columns if col != mejor_columna] + [mejor_columna]
                self.df = self.df[columnas_reordenadas]
        # ---------------------------------------------------------------------

        # Acotamos el volumen de datos a 1200 filas al azar si es masivo para calcular a mano en segundos
        if len(self.df) > 1200:
            self.df = self.df.sample(n=1200, random_state=42).reset_index(drop=True)

        columna_target = self.df.columns[-1]  # Establecemos formalmente la columna de clase definitiva
        
        # Si el objetivo tiene valores vacíos (NaN), los rellenamos con la Moda (el valor más común)
        moda_target = self.df[columna_target].mode()[0]
        self.df[columna_target] = self.df[columna_target].fillna(moda_target)

        # Filtramos dinámicamente solo las columnas que contengan datos numéricos flotantes o enteros
        columnas_numericas = self.df.select_dtypes(include=[np.number]).columns.tolist()
        if columna_target in columnas_numericas:
            columnas_numericas.remove(columna_target) # Removemos el target si se coló en los números

        # Llenamos el diccionario del EDA para alimentar la interfaz gráfica
        self.info_eda['filas_totales'] = filas_totales_original  # Para el banner superior
        self.info_eda['columnas'] = self.df.shape[1]             # Cantidad de columnas
        self.info_eda['filas_muestreo'] = self.df.shape[0]       # Mostrará las 1200 filas procesadas
        self.info_eda['distribucion_clases'] = self.df[columna_target].value_counts().to_dict() # Conteo por etiquetas
        
        # Imputación de nulos numéricos: Copiamos los datos y sustituimos vacíos por la Mediana de cada columna
        df_clean = self.df.copy()
        for col in columnas_numericas:
            mediana = df_clean[col].median()
            df_clean[col] = df_clean[col].fillna(mediana)

        # Guardamos en variables globales las matrices puras de características (X) y respuestas (y)
        self.X = df_clean[columnas_numericas].values
        self.y = pd.factorize(df_clean[columna_target])[0] # factorize convierte texto (Yes/No) a índices discretos (0, 1)

        # Calculamos la estadística fundamental del EDA: Media y Desviación Estándar de cada columna
        self.info_eda['stats'] = {
            col: (self.df[col].mean(), self.df[col].std()) for col in columnas_numericas
        }
        
        return self.info_eda  # Devolvemos el diccionario con las estadísticas del EDA

    # --- MÉTODOS DE VALIDACIÓN A MANO ---

    # Validación 1: Hold Out 70/30 Estático
    def ejecutar_hold_out_70_30(self, clf):
        np.random.seed(42)  # Semilla fija para que los experimentos sean reproducibles
        indices = np.random.permutation(len(self.X))  # Generamos una permutación aleatoria de los índices
        limite = int(len(self.X) * 0.7)  # Calculamos la frontera geométrica para el 70%
        
        train_idx, test_idx = indices[:limite], indices[limite:]  # Dividimos los índices en 70% y 30%
        
        clf.fit(self.X[train_idx], self.y[train_idx])  # Entrenamos el clasificador con el 70%
        preds = clf.predict(self.X[test_idx])          # Predecimos sobre el 30% restante
        return calcular_accuracy(self.y[test_idx], preds)  # Retornamos la precisión obtenida

    # Validación 2: Validación Cruzada de 10 Bloques (10-Fold Cross-Validation)
    def ejecutar_10_fold_cv(self, clf):
        np.random.seed(42)
        indices = np.random.permutation(len(self.X))
        folds = np.array_split(indices, 10)  # Dividimos el vector de índices aleatorios en 10 partes iguales (bloques)
        accuracies = []  # Lista para almacenar las calificaciones de las 10 iteraciones
        
        # Ciclo principal: Cada bloque fungirá como conjunto de validación una vez
        for i in range(10):
            test_idx = folds[i]  # El bloque actual se asigna a prueba
            train_idx = np.setdiff1d(indices, test_idx)  # Los otros 9 bloques se fusionan para entrenamiento
            
            clf.fit(self.X[train_idx], self.y[train_idx])  # Ajustamos el modelo con las 9 partes
            preds = clf.predict(self.X[test_idx])          # Probamos sobre la parte excluida
            accuracies.append(calcular_accuracy(self.y[test_idx], preds)) # Almacenamos el resultado de la iteración
            
        return np.mean(accuracies)  # Retornamos el promedio exacto de las 10 evaluaciones

    # Validación 3: Leave One Out (LOO) - Exclusión Individual
    def ejecutar_leave_one_out(self, clf):
        # Acotamos a 60 iteraciones consecutivas para que pinte la interfaz de forma inmediata en el examen
        limite_loo = min(60, len(self.X))
        correctos = 0  # Contador de muestras clasificadas de forma perfecta
        
        # Ciclo principal renglón por renglón
        for i in range(limite_loo):
            # Extraemos de forma geométrica el renglón número 'i' de la matriz
            X_train = np.delete(self.X[:limite_loo], i, axis=0)  # Entrenamos con todos menos el objeto 'i'
            y_train = np.delete(self.y[:limite_loo], i, axis=0)
            X_test = self.X[i].reshape(1, -1)  # Redimensionamos el elemento aislado a un vector fila de prueba
            
            clf.fit(X_train, y_train)  # Guardamos en memoria los N-1 elementos
            pred = clf.predict(X_test)[0] # Intentamos adivinar la clase del elemento aislado
            if pred == self.y[i]:
                correctos += 1  # Si acertó la clase, sumamos al contador
                
        return correctos / limite_loo  # Devolvemos la tasa final de éxito del experimento LOO
