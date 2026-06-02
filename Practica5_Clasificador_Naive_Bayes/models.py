# models.py
import pandas as pd
import numpy as np
import os

# Obtiene automáticamente la carpeta exacta donde está guardado este archivo de código
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def cargar_dataset_vino(filename='winequality-white new.csv'):
    try:
        filepath = os.path.join(BASE_DIR, filename)
        df = pd.read_csv(filepath, sep=',')
        df.columns = df.columns.str.strip()

        # Clase binaria: 1 (Buena calidad >= 6), 0 (Baja calidad < 6)
        df['Clase'] = np.where(df['quality'] >= 6, 1, 0)

        features = ['fixed acidity', 'volatile acidity', 'residual sugar', 'pH']
        X = df[features].dropna().copy()
        y = df.loc[X.index, 'Clase'].copy()
        return X, y
    except Exception as e:
        print(f"Error al cargar el dataset de vino: {e}")
        return None, None


def cargar_dataset_diamantes(filename='diamonds.csv'):
    try:
        filepath = os.path.join(BASE_DIR, filename)
        df = pd.read_csv(filepath)

        # Clase binaria respecto a la mediana del precio
        mediana_precio = df['price'].median()
        df['Clase'] = np.where(df['price'] > mediana_precio, 1, 0)

        features = ['carat', 'depth', 'table']
        X = df[features].dropna().copy()
        y = df.loc[X.index, 'Clase'].copy()

        # Reducción de tamaño para agilidad de procesamiento gráfico y bucles en GUI
        if len(X) > 3000:
            X = X.sample(3000, random_state=42)
            y = y.loc[X.index]
        return X, y
    except Exception as e:
        print(f"Error al cargar el dataset de diamantes: {e}")
        return None, None


def cargar_dataset_clima(filename='weatherAUS.csv'):
    try:
        filepath = os.path.join(BASE_DIR, filename)
        df = pd.read_csv(filepath)

        # Limpieza inicial de nulos en la etiqueta objetivo
        df = df.dropna(subset=['RainTomorrow']).copy()
        df['Clase'] = np.where(df['RainTomorrow'] == 'Yes', 1, 0)

        # Selección de variables continuas/numéricas idóneas para Gaussiana
        features = ['MinTemp', 'MaxTemp', 'Humidity3pm', 'Pressure3pm']
        df_clean = df[features + ['Clase']].dropna()

        X = df_clean[features].copy()
        y = df_clean['Clase'].copy()

        # Reducción controlada (2000 muestras) para garantizar fluidez del Hold-Out y Cross-Validation manual
        if len(X) > 2000:
            X = X.sample(2000, random_state=42)
            y = y.loc[X.index]
        return X, y
    except Exception as e:
        print(f"Error al cargar el dataset de clima: {e}")
        return None, None