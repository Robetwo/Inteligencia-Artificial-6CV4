# gui.py
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import models
import algorithms


class AppPracticaBayes:
    def __init__(self, root):
        self.root = root
        self.root.title("Práctica IA - Clasificador Naive Bayes Gaussiano")
        self.root.geometry("850x650")

        self.X = None
        self.y = None
        self.nombre_dataset = ""

        # Panel Superior de Selección
        frame_top = ttk.LabelFrame(root, text=" 1. Configuración de Datos ", padding=10)
        frame_top.pack(fill="x", padx=15, pady=10)

        ttk.Label(frame_top, text="Selecciona el Dataset:").pack(side="left", padx=5)
        self.combo_dataset = ttk.Combobox(frame_top, values=[
            "Vino Blanco (winequality-white)",
            "Diamantes (diamonds)",
            "Clima de Australia (weatherAUS)"
        ], state="readonly", width=40)
        self.combo_dataset.pack(side="left", padx=5)
        self.combo_dataset.current(0)

        btn_cargar = ttk.Button(frame_top, text="Cargar y Procesar", command=self.evento_cargar_datos)
        btn_cargar.pack(side="left", padx=10)

        # Panel de Acciones Analíticas
        self.frame_acciones = ttk.LabelFrame(root, text=" 2. Operaciones del Clasificador ", padding=10)
        self.frame_acciones.pack(fill="x", padx=15, pady=5)

        self.btn_stats = ttk.Button(self.frame_acciones, text="Calcular μ, σ y Priori",
                                    command=self.evento_estadisticos, state="disabled")
        self.btn_stats.pack(side="left", padx=5)

        self.btn_graphs = ttk.Button(self.frame_acciones, text="Ver Gráficas KDE / Gaussiana",
                                     command=self.evento_graficar, state="disabled")
        self.btn_graphs.pack(side="left", padx=5)

        self.btn_corr = ttk.Button(self.frame_acciones, text="Matriz de Correlación", command=self.evento_correlacion,
                                   state="disabled")
        self.btn_corr.pack(side="left", padx=5)

        self.btn_val = ttk.Button(self.frame_acciones, text="Validar y Comparar (HoldOut/CV/LOO)",
                                  command=self.evento_validar, state="disabled")
        self.btn_val.pack(side="left", padx=5)

        # Panel de Salida
        frame_bot = ttk.LabelFrame(root, text=" Consola de Salida de Resultados ", padding=10)
        frame_bot.pack(fill="both", expand=True, padx=15, pady=10)

        self.txt_output = scrolledtext.ScrolledText(frame_bot, wrap=tk.WORD, font=("Consolas", 10))
        self.txt_output.pack(fill="both", expand=True)

    def evento_cargar_datos(self):
        seleccion = self.combo_dataset.get()
        if "Vino" in seleccion:
            self.X, self.y = models.cargar_dataset_vino()
            self.nombre_dataset = "Vino Blanco"
        elif "Diamantes" in seleccion:
            self.X, self.y = models.cargar_dataset_diamantes()
            self.nombre_dataset = "Diamantes"
        elif "Clima" in seleccion:
            self.X, self.y = models.cargar_dataset_clima()
            self.nombre_dataset = "Clima Australia"

        if self.X is not None and len(self.X) > 0:
            self.txt_output.delete("1.0", tk.END)
            self.txt_output.insert(tk.END,
                                   f"Éxito: Dataset '{self.nombre_dataset}' cargado y limpiado correctamente.\n")
            self.txt_output.insert(tk.END,
                                   f"Dimensiones de análisis actual: {self.X.shape[0]} muestras, {self.X.shape[1]} variables continuas.\n")

            self.btn_stats["state"] = "normal"
            self.btn_graphs["state"] = "normal"
            self.btn_corr["state"] = "normal"
            self.btn_val["state"] = "normal"
        else:
            messagebox.showerror("Error",
                                 f"No se pudo encontrar o mapear el archivo asociado a la selección en la carpeta del script.")

    def evento_estadisticos(self):
        res = algorithms.obtener_estadisticos_string(self.X, self.y)
        self.txt_output.delete("1.0", tk.END)
        self.txt_output.insert(tk.END, f"=== ESTADÍSTICOS DESCRIPTIVOS: {self.nombre_dataset.upper()} ===\n\n")
        self.txt_output.insert(tk.END, res)

    def evento_graficar(self):
        self.txt_output.insert(tk.END,
                               "\nDesplegando gráficos de densidades... Revise las ventanas emergentes en su pantalla.\n")
        algorithms.generar_graficos_densidad(self.X, self.y, self.nombre_dataset)

    def evento_correlacion(self):
        res = algorithms.obtener_matrices_correlacion_string(self.X, self.y)
        self.txt_output.delete("1.0", tk.END)
        self.txt_output.insert(tk.END,
                               f"=== ANÁLISIS DE INDEPENDENCIA (CORRELACIÓN): {self.nombre_dataset.upper()} ===\n\n")
        self.txt_output.insert(tk.END, res)

    def evento_validar(self):
        self.txt_output.delete("1.0", tk.END)
        self.txt_output.insert(tk.END,
                               "Ejecutando validaciones cruzadas (Hold-Out, K-Fold, LOO)...\nPor favor espere un momento...\n\n")
        self.root.update_idletasks()
        res = algorithms.ejecutar_validaciones(self.X, self.y)
        self.txt_output.insert(tk.END, res)