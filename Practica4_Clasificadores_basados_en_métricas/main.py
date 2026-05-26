import tkinter as tk  # Importamos la librería raíz gráfica
from models import DataModel  # Enlace directo al archivo de preprocesamiento matemático
from algorithms import CustomKNN  # Enlace directo al archivo de ecuaciones de vecindad
from gui import AppGUI  # Enlace directo a la vista de interfaz de usuario

class AppController:
    # Constructor: Orquestador central. Crea las instancias de los módulos y los entrelaza
    def __init__(self):
        self.root = tk.Tk()  # Inicialización formal del bucle principal de ventanas de Tkinter
        self.model = DataModel()  # Instanciamos el modelo de datos (Capa de datos)
        self.gui = AppGUI(self.root, self.model, self)  # Instanciamos la interfaz gráfica pasándole el control central ('self')

    # Función del algoritmo de orquestación: Ejecuta secuencialmente los 7 experimentos de la rúbrica
    def generar_analisis_completo(self, metrica):
        # Vector estructurado de configuraciones dictadas en el punto 2 de la rúbrica
        configuraciones_clf = [
            {"name": "Euclidiano (K=1)", "k": 1},
            {"name": "1NN", "k": 1},
            {"name": "KNN (K=3)", "k": 3},
            {"name": "KNN (K=5)", "k": 5},
            {"name": "KNN (K=7)", "k": 7},
            {"name": "KNN (K=9)", "k": 9},
            {"name": "KNN (K=11)", "k": 11},
        ]
        
        tabla_comparativa = []  # Lista vacía que recopilará los resultados consolidados de la práctica
        
        # Bucle secuencial: Evaluamos uno por uno cada clasificador con sus 3 validaciones simultáneas
        for config in configuraciones_clf:
            # Creamos la instancia de nuestro KNN personalizado pasándole el K y la distancia activa
            clf = CustomKNN(k=config['k'], metric=metrica)
            
            # Mandamos el objeto clasificador a los métodos matemáticos del modelo para calcular el Accuracy a mano
            acc_ho = self.model.ejecutar_hold_out_70_30(clf)  # Validación A
            acc_kf = self.model.ejecutar_10_fold_cv(clf)      # Validación B
            acc_loo = self.model.ejecutar_leave_one_out(clf)  # Validación C
            
            # Guardamos los porcentajes formateados a dos decimales y con su símbolo de porciento
            tabla_comparativa.append({
                "clf": config['name'],
                "ho": f"{acc_ho * 100:.2f}%",
                "kf": f"{acc_kf * 100:.2f}%",
                "loo": f"{acc_loo * 100:.2f}%"
            })
            
        # Una vez completo el maratón de cómputo, le enviamos la tabla final estructurada a la interfaz para que la dibuje
        self.gui.mostrar_tabla_final(tabla_comparativa)

    # Lanzador del sistema: Arranca el hilo de ejecución infinita de la interfaz de usuario
    def run(self):
        self.root.mainloop()  # Mantiene la ventana abierta escuchando los eventos de los clics

# Punto de entrada de Python estándar
if __name__ == "__main__":
    app = AppController()  # Inicializamos nuestro controlador general
    app.run()  # Encendemos el motor visual
