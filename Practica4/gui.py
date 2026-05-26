import tkinter as tk  # Librería estándar para crear ventanas y contenedores gráficos nativos
from tkinter import filedialog, ttk  # Herramientas para abrir el explorador de archivos y usar temas estilizados
import matplotlib.pyplot as plt  # Biblioteca para modelar curvas estadísticas y planos cartesianos
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # Conector para incrustar figuras de Matplotlib en Tkinter
import numpy as np  # Usado para contar las clases independientes en los gráficos

class AppGUI:
    # Constructor: Diseña los cimientos, dimensiones de la ventana y el set de colores (Style)
    def __init__(self, root, model, controller):
        self.root = root  # Enlace de la ventana raíz de Tkinter
        self.model = model  # Enlace al modelo de datos
        self.controller = controller  # Enlace al controlador del sistema
        
        self.root.title("ESCOM - Inteligencia Artificial | Práctica 4")  # Título de la app
        self.root.geometry("1000x800")  # Dimensiones fijas iniciales en píxeles (Ancho x Alto)
        self.root.configure(bg="#f8f9fa")  # Color de fondo de la ventana principal
        
        # Inicialización y configuración del gestor de temas 'ttk'
        self.style = ttk.Style()
        self.style.theme_use("clam")  # Usamos el motor visual 'clam' por ser el más personalizable
        
        # Configuración global de paletas y fuentes para contenedores
        self.style.configure(".", background="#f8f9fa", foreground="#333333", font=("Segoe UI", 10))
        self.style.configure("TLabelframe", background="#ffffff", relief="flat", borderwidth=1)
        self.style.configure("TLabelframe.Label", background="#ffffff", foreground="#495057", font=("Segoe UI", 10, "bold"))
        
        # Diseño personalizado para el Botón de Cómputo (Estilo Acero/Azul)
        self.style.configure("Accent.TButton", background="#0275d8", foreground="#ffffff", font=("Segoe UI", 10, "bold"), padding=6)
        self.style.map("Accent.TButton", background=[("active", "#025aa5"), ("disabled", "#e9ecef")], foreground=[("disabled", "#adb5bd")])
        
        # Diseño personalizado para Botones Secundarios (Gris Industrial)
        self.style.configure("Secondary.TButton", background="#6c757d", foreground="#ffffff", font=("Segoe UI", 10), padding=6)
        self.style.map("Secondary.TButton", background=[("active", "#5a6268")])

        # Diseño para la Cuadrícula Treeview (Formato de filas limpias tipo Excel)
        self.style.configure("Treeview", font=("Segoe UI", 10), rowheight=26, background="#ffffff", fieldbackground="#ffffff")
        self.style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#e9ecef", foreground="#495057")
        self.style.map("Treeview", background=[("selected", "#0275d8")], foreground=[("selected", "#ffffff")])

        self._crear_componentes()  # Llamamos al sub-constructor que dibuja los botones y paneles

    # Función interna encargada del dibujo y empaquetado de widgets en la UI
    def _crear_componentes(self):
        # Encabezado Superior (Banner Premium Gris Oscuro)
        header_frame = tk.Frame(self.root, bg="#212529", height=60)
        header_frame.pack(fill="x", side="top")
        header_frame.pack_propagate(False)  # Evita que el contenedor se deforme por el tamaño del texto
        
        lbl_title = tk.Label(header_frame, text="Clasificadores Basados en Métricas de Distancia", bg="#212529", fg="#ffffff", font=("Segoe UI", 14, "bold"))
        lbl_title.pack(side="left", padx=20, pady=15)
        
        lbl_sub = tk.Label(header_frame, text="Práctica 4", bg="#212529", fg="#a8aeb4", font=("Segoe UI", 10, "italic"))
        lbl_sub.pack(side="right", padx=20, pady=18)

        # Área Central de Trabajo (Margen de separación)
        main_container = tk.Frame(self.root, bg="#f8f9fa")
        main_container.pack(fill="both", expand=True, padx=20, pady=15)

        # 1. CONTENEDOR SUPERIOR: BOTONES DE ARCHIVO
        frame_top = ttk.LabelFrame(main_container, text=" 1. Origen de Datos ", padding=15)
        frame_top.pack(fill="x", pady=(0, 10))
        
        self.btn_cargar = ttk.Button(frame_top, text="📂 Buscar Dataset (.csv)", style="Secondary.TButton", command=self._evento_cargar)
        self.btn_cargar.pack(side="left", padx=(5, 15))
        
        self.btn_graficar = ttk.Button(frame_top, text="📊 Visualizar Gráficas 2D (EDA)", style="Secondary.TButton", state="disabled", command=self._abrir_ventana_graficas)
        self.btn_graficar.pack(side="left", padx=5)
        
        self.lbl_status = ttk.Label(frame_top, text="Ningún archivo seleccionado en el sistema.", font=("Segoe UI", 10, "italic"), foreground="#6c757d")
        self.lbl_status.pack(side="left", fill="x", expand=True, padx=15)

        # 2. CONTENEDOR CENTRAL: SELECTOR DE DISTANCIAS
        frame_mid = ttk.LabelFrame(main_container, text=" 2. Configuración del Experimento ", padding=15)
        frame_mid.pack(fill="x", pady=10)
        
        ttk.Label(frame_mid, text="Función de Distancia:", font=("Segoe UI", 10)).pack(side="left", padx=5)
        
        # Menú desplegable combobox con las 4 opciones solicitadas
        self.combo_metrica = ttk.Combobox(frame_mid, values=["Euclidiana (L2)", "Manhattan (L1)", "Chebyshev (Linf)", "Camberra (No-Minkowski)"], state="readonly", width=25)
        self.combo_metrica.current(0)  # Establece Euclidiana por defecto
        self.combo_metrica.pack(side="left", padx=10)

        self.btn_ejecutar = ttk.Button(frame_mid, text="⚡ Construir Tabla Comparativa", style="Accent.TButton", state="disabled", command=self._evento_ejecutar)
        self.btn_ejecutar.pack(side="right", padx=5)

        # 3. CONTENEDOR INFERIOR: ÁREA MULTI-PESTAÑAS (NOTEBOOK)
        frame_bot = ttk.LabelFrame(main_container, text=" 3. Resultados del Cómputo e Historial EDA ", padding=15)
        frame_bot.pack(fill="both", expand=True, pady=10)

        notebook = ttk.Notebook(frame_bot)  # Control de pestañas nativo de ttk
        notebook.pack(fill="both", expand=True)

        # Pestaña A: Cuadrícula Interactiva para el Punto 5
        tab_tabla = ttk.Frame(notebook)
        notebook.add(tab_tabla, text=" 📊 Tabla Comparativa   ")
        
        columnas = ("clf", "ho", "kf", "loo")  # Identificadores de las columnas de datos
        self.tree = ttk.Treeview(tab_tabla, columns=columnas, show="headings")  # show="headings" oculta la columna vacía inicial
        self.tree.heading("clf", text="Clasificador")
        self.tree.heading("ho", text="Hold Out 70/30")
        self.tree.heading("kf", text="10-Fold Cross-Validation")
        self.tree.heading("loo", text="Leave One Out")
        
        # Ajuste de anchos individuales en pixeles y alineación de textos
        self.tree.column("clf", width=180, anchor="w")
        self.tree.column("ho", width=140, anchor="center")
        self.tree.column("kf", width=160, anchor="center")
        self.tree.column("loo", width=140, anchor="center")
        
        # Registramos las etiquetas de color para el efecto cebra intercalado
        self.tree.tag_configure("par", background="#ffffff")
        self.tree.tag_configure("impar", background="#f1f3f5")
        
        scroll_tree = ttk.Scrollbar(tab_tabla, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_tree.set)
        scroll_tree.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)

        # Pestaña B: Área de Texto Monoespaciada para el Reporte Estadístico del EDA
        tab_eda = ttk.Frame(notebook)
        notebook.add(tab_eda, text=" 📝 Reporte Estadístico EDA   ")
        
        self.txt_eda = tk.Text(tab_eda, wrap="none", font=("Consolas", 10), bg="#ffffff", fg="#212529", relief="flat")
        scroll_txt = ttk.Scrollbar(tab_eda, orient="vertical", command=self.txt_eda.yview)
        self.txt_eda.configure(yscrollcommand=scroll_txt.set)
        scroll_txt.pack(side="right", fill="y")
        self.txt_eda.pack(fill="both", expand=True, padx=5, pady=5)

    # Disparador del Botón Cargar: Invoca al explorador de archivos de Windows/Linux
    def _evento_cargar(self):
        ruta = filedialog.askopenfilename(filetypes=[("Archivos CSV", "*.csv")])
        if ruta:
            info = self.model.cargar_y_limpiar_dataset(ruta)  # Mandamos la ruta física al modelo para que la procese
            
            # Pintamos de color verde la notificación con el tamaño total original del archivo
            self.lbl_status.config(
                text=f"✔ Dataset listo: {info['filas_totales']} filas | {info['columnas']} columnas.", 
                foreground="#28a745"
            )
            self.btn_ejecutar.config(state="normal")  # Habilitamos el botón de procesamiento
            self.btn_graficar.config(state="normal")  # Habilitamos el botón de gráficas 2D
            
            # Limpiamos e imprimimos el cuadro del reporte estadístico del EDA
            self.txt_eda.delete("1.0", tk.END)
            self.txt_eda.insert(tk.END, f"=================================================================\n")
            self.txt_eda.insert(tk.END, f"        REPORTE ANALÍTICO DE EXPLORACIÓN DE DATOS (EDA)\n")
            self.txt_eda.insert(tk.END, f"=================================================================\n\n")
            self.txt_eda.insert(tk.END, f"-> Cantidad de instancias procesadas: {info['filas_muestreo']} filas.\n")
            self.txt_eda.insert(tk.END, f"-> Frecuencia de Etiquetas en Target: {info['distribucion_clases']}\n\n")
            self.txt_eda.insert(tk.END, f"{'Atributo Continuo':<25} | {'Media Matemática':<18} | {'Desviación Estándar'}\n")
            self.txt_eda.insert(tk.END, "-" * 75 + "\n")
            # Ciclo que recorre el diccionario imprimiendo la media y desviación estándar de cada atributo numérico
            for col, stats in info['stats'].items():
                self.txt_eda.insert(tk.END, f"{col[:25]:<25} | {stats[0]:<18.4f} | {stats[1]:.4f}\n")

    # Disparador del Botón de Gráficas: Genera la sub-ventana flotante independiente para el Punto 1.e
    def _abrir_ventana_graficas(self):
        if self.model.X is None:
            return  # Verificación de seguridad si no hay datos en memoria
            
        ventana_graficos = tk.Toplevel(self.root)  # Crea un contenedor flotante hijo de tipo Toplevel
        ventana_graficos.title("Punto 1.e: Gráficas de Atributos Agrupados por Clases")
        ventana_graficos.geometry("850x500")
        ventana_graficos.configure(bg="#ffffff")

        X_data = self.model.X
        y_data = self.model.y
        clases_unicas = np.unique(y_data)  # Extrae un vector único con el número real de clases (ej: 0, 1 o del 0 al 6)
        
        # Creamos una figura de Matplotlib estructurada en 1 renglón con 2 columnas (dos paneles gráficos)
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
        
        # --- PANEL GRÁFICO 1: Scatter Plot (Dispersión 2D) ---
        # Cruza el Atributo 1 contra el Atributo 2 en los ejes X e Y, y los pinta según su etiqueta de clase ('c=y_data')
        scatter = ax1.scatter(X_data[:, 0], X_data[:, 1], c=y_data, cmap="tab10", alpha=0.7, edgecolors='none')
        ax1.set_title("Dispersión de Atributos por Clase", fontsize=10, fontweight="bold")
        ax1.set_xlabel("Atributo Continuo 1", fontsize=9)
        ax1.set_ylabel("Atributo Continuo 2", fontsize=9)
        ax1.grid(True, linestyle="--", alpha=0.5)
        
        # Generamos la caja de leyendas que asocia los círculos de colores con su número de clase real
        legend1 = ax1.legend(*scatter.legend_elements(), title="Clases", loc="upper right")
        ax1.add_artist(legend1)

        # --- PANEL GRÁFICO 2: Boxplot Dinámico Multiclase (Adaptativo para cualquier CSV) ---
        if X_data.shape[1] > 2:
            datos_por_clase = []
            etiquetas_cajas = []
            # Recorremos cada clase identificada e indexamos únicamente sus registros correspondientes al atributo 3
            for c in clases_unicas:
                datos_por_clase.append(X_data[y_data == c, 2])
                etiquetas_cajas.append(f"Clase {c}")
            
            # Dibujamos de golpe tantas cajas de bigotes como elementos agrupados existan en la lista
            ax2.boxplot(datos_por_clase, labels=etiquetas_cajas)
            ax2.set_title("Distribución del Atributo 3 por Clase", fontsize=10, fontweight="bold")
            ax2.set_ylabel("Valores del Atributo", fontsize=9)
        else:
            # Plan B por seguridad si el CSV tuviera apenas dos columnas
            ax2.scatter(X_data[:, 0], y_data, c=y_data, cmap="tab10", alpha=0.5)
            ax2.set_title("Mapeo Relativo Unidimensional", fontsize=10)
            
        ax2.grid(True, linestyle="--", alpha=0.5)
        fig.tight_layout()  # Ajusta los márgenes automáticamente para evitar colisiones de texto

        # Acoplamos el lienzo matemático de Matplotlib convirtiéndolo en un widget compatible con Tkinter
        canvas = FigureCanvasTkAgg(fig, master=ventana_graficos)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    # Disparador del Botón de Cómputo: Desactiva el control momentáneamente y manda llamar al controlador
    def _evento_ejecutar(self):
        metrica = self.combo_metrica.get()
        self.btn_ejecutar.config(state="disabled") # Deshabilitamos para prevenir clics dobles mientras computa a mano
        self.root.update()  # Forzamos la actualización visual inmediata de la interfaz
        self.controller.generar_analisis_completo(metrica)  # Ejecutamos el lazo de experimentos
        self.btn_ejecutar.config(state="normal") # Volvemos a habilitar el botón al finalizar

    # Inyección final: Recibe la lista estructurada del controlador y llena la tabla Grid visual
    def mostrar_tabla_final(self, matriz_resultados):
        # Ciclo para limpiar cualquier renglón remanente de una ejecución previa
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Recorremos la matriz e insertamos los renglones aplicando las propiedades cebra (par/impar)
        for i, row in enumerate(matriz_resultados):
            tag_color = "par" if i % 2 == 0 else "impar"
            self.tree.insert("", "end", values=(row['clf'], row['ho'], row['kf'], row['loo']), tags=(tag_color,))
