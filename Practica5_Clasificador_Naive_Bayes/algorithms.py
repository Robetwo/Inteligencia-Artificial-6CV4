# algorithms.py
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import norm
from sklearn.model_selection import train_test_split, KFold, LeaveOneOut
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score

class MiNaiveBayesGaussiano:
    def fit(self, X, y):
        self.clases = np.unique(y)
        self.p_priori = {}
        self.medias = {}
        self.desviaciones = {}
        total_muestras = len(y)

        for c in self.clases:
            X_c = X[y == c]
            self.p_priori[c] = len(X_c) / total_muestras
            self.medias[c] = X_c.mean(axis=0).to_dict()
            # Se suma 1e-9 (épsilon) para evitar divisiones matemáticas indeterminadas por cero
            self.desviaciones[c] = (X_c.std(axis=0) + 1e-9).to_dict()

    def _calcular_verosimilitud(self, x_val, media, desv):
        exponente = np.exp(-((x_val - media) ** 2) / (2 * (desv ** 2)))
        return (1 / (np.sqrt(2 * np.pi) * desv)) * exponente

    def predict(self, X):
        predicciones = []
        for _, fila in X.iterrows():
            mejores_probabilidades = {}
            for c in self.clases:
                prob_clase = self.p_priori[c]
                for col in X.columns:
                    x_val = fila[col]
                    media = self.medias[c][col]
                    desv = self.desviaciones[c][col]
                    prob_clase *= self._calcular_verosimilitud(x_val, media, desv)
                mejores_probabilidades[c] = prob_clase
            clase_predicha = max(mejores_probabilidades, key=mejores_probabilidades.get)
            predicciones.append(clase_predicha)
        return np.array(predicciones)


def obtener_estadisticos_string(X, y):
    clases = np.unique(y)
    total_instancias = len(y)
    output = "--- PROBABILIDADES A PRIORI ---\n"
    for c in clases:
        p_priori = np.sum(y == c) / total_instancias
        output += f"P(Clase {c}): {p_priori:.4f}\n"

    output += "\n--- PARÁMETROS POR CARACTERÍSTICA (μ y σ) ---\n"
    for col in X.columns:
        output += f"Variable: '{col}'\n"
        for c in clases:
            datos_clase = X[y == c][col]
            output += f"  [Clase {c}] μ (Media): {datos_clase.mean():.4f} | σ (Desv. Est): {datos_clase.std():.4f}\n"
    return output


def generar_graficos_densidad(X, y, nombre_dataset):
    clases = np.unique(y)
    for col in X.columns:
        plt.figure(figsize=(6, 3.5))
        for c in clases:
            datos_clase = X[y == c][col].dropna()
            sns.kdeplot(datos_clase, label=f'Clase {c} (KDE Real)', linewidth=2)

            mu, std = datos_clase.mean(), datos_clase.std()
            xmin, xmax = plt.xlim()
            x_eje = np.linspace(xmin, xmax, 100)
            plt.plot(x_eje, norm.pdf(x_eje, mu, std), linestyle='--', label=f'Clase {c} (Gaussiana)')

        plt.title(f"{nombre_dataset} - '{col}'")
        plt.xlabel(col)
        plt.ylabel("Densidad")
        plt.legend()
        plt.tight_layout()
        plt.show()


def obtener_matrices_correlacion_string(X, y):
    clases = np.unique(y)
    output = ""
    for c in clases:
        output += f"--- Matriz de Correlación - Clase {c} ---\n"
        matriz = X[y == c].corr().round(3)
        output += matriz.to_string() + "\n\n"
    return output


def ejecutar_validaciones(X, y):
    modelo_propio = MiNaiveBayesGaussiano()
    modelo_sklearn = GaussianNB()

    # 1. Hold-Out 80/20
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)
    modelo_propio.fit(X_train, y_train)
    acc_propio_ho = accuracy_score(y_test, modelo_propio.predict(X_test))

    modelo_sklearn.fit(X_train, y_train)
    acc_sklearn_ho = accuracy_score(y_test, modelo_sklearn.predict(X_test))

    # 2. 10-Fold CV
    kf = KFold(n_splits=10, shuffle=True, random_state=42)
    accs_p_kf, accs_sk_kf = [], []
    for train_idx, test_idx in kf.split(X):
        X_tr, X_te = X.iloc[train_idx], X.iloc[test_idx]
        y_tr, y_te = y.iloc[train_idx], y.iloc[test_idx]

        modelo_propio.fit(X_tr, y_tr)
        accs_p_kf.append(accuracy_score(y_te, modelo_propio.predict(X_te)))

        modelo_sklearn.fit(X_tr, y_tr)
        accs_sk_kf.append(accuracy_score(y_te, modelo_sklearn.predict(X_te)))

    # 3. Leave-One-Out (Submuestra fija de 150 elementos para respuesta interactiva instantánea)
    X_sub, _, y_sub, _ = train_test_split(X, y, train_size=150, random_state=42, stratify=y)
    loo = LeaveOneOut()
    accs_p_loo, accs_sk_loo = [], []
    for train_idx, test_idx in loo.split(X_sub):
        X_tr, X_te = X_sub.iloc[train_idx], X_sub.iloc[test_idx]
        y_tr, y_te = y_sub.iloc[train_idx], y_sub.iloc[test_idx]

        modelo_propio.fit(X_tr, y_tr)
        accs_p_loo.append(accuracy_score(y_te, modelo_propio.predict(X_te)))

        modelo_sklearn.fit(X_tr, y_tr)
        accs_sk_loo.append(accuracy_score(y_te, modelo_sklearn.predict(X_te)))

    res = (
        "=== RESULTADOS DE VALIDACIÓN (Exactitud / Accuracy) ===\n\n"
        f"[Hold-Out 80/20]\n"
        f"  -> Modelo Propio:  {acc_propio_ho:.4f}\n"
        f"  -> Scikit-Learn:  {acc_sklearn_ho:.4f}\n\n"
        f"[10-Fold Cross Validation (Promedio)]\n"
        f"  -> Modelo Propio:  {np.mean(accs_p_kf):.4f}\n"
        f"  -> Scikit-Learn:  {np.mean(accs_sk_kf):.4f}\n\n"
        f"[Leave-One-Out (Muestra N=150)]\n"
        f"  -> Modelo Propio:  {np.mean(accs_p_loo):.4f}\n"
        f"  -> Scikit-Learn:  {np.mean(accs_sk_loo):.4f}\n"
    )
    return res