import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import random
import os
from PIL import Image, ImageTk
from solvers import AStarPuzzleSolver

class PuzzleApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        # --- CONFIGURACIÓN DE LA VENTANA PRINCIPAL ---
        self.title("N-Puzzle - Solucionador A*")
        self.geometry("800x600")

        # Variables de estado del juego
        self.size = 3              # Tamaño por defecto (3x3 para el 8-puzzle)
        self.current_state = None  # Almacena la matriz actual del tablero
        self.cells = {}            # Diccionario para referenciar los widgets del tablero
        self.image_pieces = []     # Lista de recortes de la imagen
        self.base_image = None     # Imagen original cargada

        # --- RECURSOS ---
        # Lista de imágenes que el programa buscará en la carpeta local
        self.image_files = ["1.jpg", "2.jpg", "3.jpg",
                            "4.jpg", "5.jpg", "6.jpg",
                            "7.jpg", "8.jpg"]
        self.current_image_index = 0

        # Inicialización de la interfaz
        self.setup_styles()        # Estilos visuales para la tabla de datos
        self.setup_ui()            # Construcción de botones y paneles
        self.load_local_image()    # Carga y procesamiento de imagen
        self.generate_puzzle()     # Creación del primer tablero mezclado

    def setup_styles(self):
        """Define la apariencia visual de la tabla (Treeview) donde se ven los resultados."""
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2b2b2b", foreground="white", 
                        fieldbackground="#2b2b2b", font=("Segoe UI", 12))
        style.configure("Treeview.Heading", background="#1f1f1f", foreground="white", 
                        font=("Segoe UI", 14, "bold"))
        style.map("Treeview", background=[('selected', '#3498db')])
        style.configure("Treeview", rowheight=30)

    def setup_ui(self):
        """Organiza la estructura de la ventana: Barra lateral y Zona de juego."""
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- PANEL LATERAL (CONTROLES) ---
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # Título de la App
        title_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        title_frame.pack(pady=20)
        ctk.CTkLabel(title_frame, text="N", font=ctk.CTkFont(size=28, weight="bold")).grid(row=0, column=0)
        ctk.CTkLabel(title_frame, text="Puzzle", text_color="yellow", 
                     font=ctk.CTkFont(size=28, weight="bold")).grid(row=0, column=1, padx=5)

        # Configuración del tamaño (3x3 o 4x4)
        ctk.CTkLabel(self.sidebar, text="Configuración", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        self.puzzle_type = ctk.CTkSegmentedButton(self.sidebar, values=["3x3 (8)", "4x4 (15)"], 
                                                  command=self.change_size)
        self.puzzle_type.set("3x3 (8)")
        self.puzzle_type.pack(padx=20, pady=10)

        # Botones de acción
        self.btn_change_img = ctk.CTkButton(self.sidebar, text="CAMBIAR FOTO", fg_color="#34495e", 
                                            command=self.cycle_image)
        self.btn_change_img.pack(pady=2, padx=20)

        self.btn_random = ctk.CTkButton(self.sidebar, text="MEZCLAR", fg_color="#CF530A", 
                                        command=self.generate_puzzle)
        self.btn_random.pack(pady=2, padx=20)

        # Selección de Heurística (El "motor" de decisión de la IA)
        ctk.CTkLabel(self.sidebar, text="Heurística:", font=("bold", 14)).pack(pady=10)
        self.h_var = ctk.StringVar(value="Manhattan")
        ctk.CTkOptionMenu(self.sidebar, values=["Fichas fuera", "Manhattan", "Weighted A*"], 
                          variable=self.h_var).pack(pady=10)

        self.btn_solve = ctk.CTkButton(self.sidebar, text="RESOLVER", height=50, 
                                       font=ctk.CTkFont(size=14, weight="bold"), 
                                       fg_color="#149900", command=self.run_ai)
        self.btn_solve.pack(pady=2, padx=20)

        # --- CONTENEDOR CENTRAL (TABLERO Y TABLA) ---
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=0, pady=5)

        self.game_zone = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.game_zone.pack(pady=5)

        # Previsualización de la Meta (Estado Objetivo)
        self.target_frame = ctk.CTkFrame(self.game_zone, fg_color="#1a1a1a", border_width=2, border_color="#444")
        self.target_frame.grid(row=0, column=0, padx=5, sticky="n")
        ctk.CTkLabel(self.target_frame, text="META", font=("Segoe UI", 12, "bold")).pack(pady=5)
        self.preview_label = tk.Label(self.target_frame, bg="#1a1a1a")
        self.preview_label.pack(padx=10, pady=10)

        # Cuadrícula del juego
        self.grid_frame = ctk.CTkFrame(self.game_zone, fg_color="#121212", border_width=3, border_color="#555")
        self.grid_frame.grid(row=0, column=1, padx=5)

        # Tabla inferior de estadísticas de rendimiento
        self.tree_frame = ctk.CTkFrame(self.main_container)
        self.tree_frame.pack(fill="x", side="bottom", pady=0)

        cols = ("H", "T", "M", "S")
        self.tree = ttk.Treeview(self.tree_frame, columns=cols, show="headings", height=4)
        for c, h in zip(self.tree["columns"], ["Heurística", "Tiempo (ms)", "Memoria (KB)", "Pasos"]):
            self.tree.heading(c, text=h)
            self.tree.column(c, width=100, anchor="center")
        self.tree.pack(fill="both", expand=True)

    def load_local_image(self):
        """Carga una imagen, la recorta a cuadrado y la divide en piezas."""
        filename = self.image_files[self.current_image_index]
        if not os.path.exists(filename):
            messagebox.showerror("Error", f"No se encontró {filename}")
            return

        img = Image.open(filename)
        # Recorte central (Crop) para mantener la relación de aspecto cuadrada
        w, h = img.size
        min_dim = min(w, h)
        left, top = (w - min_dim) / 2, (h - min_dim) / 2
        img = img.crop((left, top, left + min_dim, top + min_dim))

        # Tamaño del lienzo del juego
        canvas_size = 540
        self.base_image = img.resize((canvas_size, canvas_size), Image.Resampling.LANCZOS)

        # Actualizar vista previa pequeña
        preview_tk = ImageTk.PhotoImage(self.base_image.resize((150, 150)))
        self.preview_label.config(image=preview_tk)
        self.preview_label.image = preview_tk

        self.slice_image() # Cortar la imagen en piezas según self.size

    def slice_image(self):
        """Divide la imagen base en cuadritos dependiendo de si es 3x3 o 4x4."""
        self.image_pieces = []
        p_size = self.base_image.size[0] // self.size
        for r in range(self.size):
            for c in range(self.size):
                left, top = c * p_size, r * p_size
                piece = self.base_image.crop((left, top, left + p_size, top + p_size))
                # Añadir un pequeño borde oscuro a cada pieza
                bordered = Image.new('RGB', (p_size, p_size), "#333333")
                bordered.paste(piece, (1, 1))
                self.image_pieces.append(ImageTk.PhotoImage(bordered))

    def generate_puzzle(self):
        """Crea un puzzle mezclado garantizando que sea SOLUBLE."""
        for widget in self.grid_frame.winfo_children(): widget.destroy()
        self.cells = {}

        # Empezamos desde el estado meta (ordenado)
        state = np.arange(1, self.size ** 2 + 1).reshape(self.size, self.size)
        state[-1, -1] = 0
        r, c = self.size - 1, self.size - 1

        # Realizamos movimientos aleatorios válidos para "desordenar" el puzzle.
        # Esto evita generar puzzles insolubles (problema de paridad).
        moves = 40 if self.size == 3 else 80
        for _ in range(moves):
            dr, dc = random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.size and 0 <= nc < self.size:
                state[r, c], state[nr, nc] = state[nr, nc], state[r, c]
                r, c = nr, nc

        self.current_state = state
        
        # Crear los widgets visuales (Canvas) para cada celda
        p_size = self.base_image.size[0] // self.size
        for r in range(self.size):
            for c in range(self.size):
                canv = tk.Canvas(self.grid_frame, width=p_size - 1, height=p_size - 1,
                                 bg="#121212", highlightthickness=1, highlightbackground="#333")
                canv.grid(row=r, column=c)
                img_id = canv.create_image(0, 0, anchor="nw")
                self.cells[(r, c)] = (canv, img_id)
        self.update_display()

    def update_display(self, state=None):
        """Refresca las imágenes en el tablero según la matriz de números actual."""
        target = state if state is not None else self.current_state
        for r in range(self.size):
            for c in range(self.size):
                val = target[r, c]
                canv, img_canvas_id = self.cells[(r, c)]
                if val == 0: # El espacio vacío no muestra imagen
                    canv.itemconfig(img_canvas_id, image="")
                else:
                    img_tk = self.image_pieces[val - 1]
                    canv.itemconfig(img_canvas_id, image=img_tk)
                    canv.image_ref = img_tk # Evitar que el recolector de basura borre la imagen

    def animate_path(self, path):
        """Muestra paso a paso la solución encontrada por la IA."""
        def step(i):
            if i < len(path):
                # Actualiza visualmente el tablero al estado i del camino
                self.update_display(np.array(path[i]).reshape(self.size, self.size))
                # Esperar 200 milisegundos para el siguiente movimiento
                self.after(200, lambda: step(i + 1))
            else:
                self.btn_solve.configure(state="normal") # Reactiva el botón al finalizar

        self.btn_solve.configure(state="disabled") # Bloquea el botón durante la animación
        step(0)

    def run_ai(self):
        """Llama al algoritmo A* y procesa los resultados de rendimiento."""
        h = self.h_var.get()
        # Inicializar el solucionador con el estado actual del tablero
        solver = AStarPuzzleSolver(self.current_state, self.size, h)
        
        # Ejecutar búsqueda (devuelve éxito, camino, tiempo y memoria)
        success, path, t, m = solver.solve()
        
        if success:
            # Registrar resultados en la tabla comparativa
            self.tree.insert("", 0, values=(h, f"{t:.4f}", f"{m:.1f}", len(path) - 1))
            self.animate_path(path)
        else:
            messagebox.showwarning("IA", "Insoluble o límite de búsqueda excedido.")

    def cycle_image(self):
        """Cambia a la siguiente imagen de la lista y reinicia el puzzle."""
        self.current_image_index = (self.current_image_index + 1) % len(self.image_files)
        self.load_local_image()
        self.generate_puzzle()

    def change_size(self, val):
        """Ajusta el tamaño del tablero (3x3 o 4x4) y regenera las piezas."""
        self.size = 3 if "3x3" in val else 4
        self.slice_image()
        self.generate_puzzle()
