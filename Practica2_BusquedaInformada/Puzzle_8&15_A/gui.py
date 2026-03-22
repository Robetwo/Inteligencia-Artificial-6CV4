import customtkinter as ctk             # Librería para la interfaz moderna (botones redondeados, temas oscuros)
import tkinter as tk                    # Librería base de interfaces en Python
from tkinter import ttk, messagebox     # ttk para widgets clásicos (tablas) y messagebox para alertas
import numpy as np                      # Manejo de matrices numéricas (el tablero es una matriz)
import random                           # Para elegir movimientos al azar al mezclar
import os                               # Para verificar si las imágenes existen en la carpeta
from PIL import Image, ImageTk          # Procesamiento de imágenes (recortar, redimensionar)
from solvers import AStarPuzzleSolver   # Importa la lógica de IA desde el otro archivo

# Definición de la ventana principal en CustomTkinter
class PuzzleApp(ctk.CTk):

    def __init__(self):
        super().__init__()  # Inicializa la ventana padre

        # --- Configuración básica de la ventana ---
        self.title("N-Puzzle - A*")  # Título de la aplicación
        self.geometry("800x580")  # Tamaño inicial en píxeles

        # --- Variables de estado del juego ---
        self.size = 3               # Tamaño por defecto (3x3)
        self.current_state = None   # Guardará la matriz actual del puzzle
        self.cells = {}             # Diccionario para rastrear los cuadros de la interfaz
        self.image_pieces = []      # Lista con los recortes de la imagen
        self.base_image = None      # La imagen completa cargada

        # --- Lista de nombres de archivos de imagen esperados en la carpeta ---
        self.image_files = ["1.jpg", "2.jpg", "3.jpg",
                            "4.jpg", "5.jpg", "6.jpg",
                            "7.jpg", "8.jpg"]

        # Índice para saber qué imagen de la lista mostrar
        self.current_image_index = 0

        # --- Llamadas a funciones de inicialización ---
        self.setup_styles()         # Configura el aspecto visual de las tablas
        self.setup_ui()             # Crea todos los botones y paneles
        self.load_local_image()     # Carga la primera imagen
        self.generate_puzzle()      # Crea y mezcla el primer tablero

    # Configura el estilo visual de la tabla (Treeview) de estadísticas
    def setup_styles(self):

        style = ttk.Style()
        style.theme_use("default")  # Usa el tema base para poder sobreescribirlo

        # Colores oscuros para la tabla de resultados (fondo gris, letra blanca)
        style.configure("Treeview",
                        background="#2b2b2b",
                        foreground="white",
                        fieldbackground="#2b2b2b",
                        font=("Segoe UI", 12))

        # Estilo de los encabezados de la tabla
        style.configure("Treeview.Heading",
                        background="#1f1f1f",
                        foreground="white",
                        font=("Segoe UI", 14, "bold"))

        # Color azul cuando seleccionas una fila de la tabla
        style.map("Treeview",
                  background=[('selected', '#3498db')])

        style.configure("Treeview", rowheight=30)  # Altura de cada fila

    # Crea y organiza todos los componentes visuales (Botones, Paneles)
    def setup_ui(self):

        # Configuración de la cuadrícula principal de la ventana (2 columnas)
        self.grid_columnconfigure(1, weight=1)  # La columna derecha se expande
        self.grid_rowconfigure(0, weight=1)  # La fila se expande verticalmente

        # --- BARRA LATERAL (Panel de control izquierdo) ---
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # Título "N-Puzzle"
        title_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        title_frame.pack(pady=20)

        ctk.CTkLabel(title_frame,
                     text="N",
                     font=ctk.CTkFont(size=28, weight="bold")).grid(row=0, column=0)

        ctk.CTkLabel(title_frame,
                     text="Puzzle",
                     text_color="yellow",
                     font=ctk.CTkFont(size=28, weight="bold")).grid(row=0, column=1, padx=5)

        # Sección de Configuración
        ctk.CTkLabel(self.sidebar,
                     text="Configuración",
                     font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        ctk.CTkLabel(self.sidebar,
                     text="Tamaño:",
                     font=("bold", 14)).pack(pady=10)

        # Botón segmentado para elegir entre 3x3 o 4x4
        self.puzzle_type = ctk.CTkSegmentedButton(self.sidebar,
                                                  values=["3x3 (8)", "4x4 (15)"],
                                                  font=ctk.CTkFont(size=14, weight="bold"),
                                                  command=self.change_size)

        self.puzzle_type.set("3x3 (8)")
        self.puzzle_type.pack(padx=20, pady=10)

        # Botón para cambiar a la siguiente foto de la lista
        self.btn_change_img = ctk.CTkButton(self.sidebar,
                                            text="CAMBIAR FOTO",
                                            height=45,
                                            font=ctk.CTkFont(size=14, weight="bold"),
                                            fg_color="#34495e",
                                            command=self.cycle_image)

        self.btn_change_img.pack(pady=2, padx=20)

        # Botón para mezclar el puzzle actual
        self.btn_random = ctk.CTkButton(self.sidebar,
                                        text="MEZCLAR",
                                        height=45,
                                        font=ctk.CTkFont(size=14, weight="bold"),
                                        fg_color="#CF530A",
                                        command=self.generate_puzzle)

        self.btn_random.pack(pady=2, padx=20)

        ctk.CTkLabel(self.sidebar, text="", font=ctk.CTkFont(size=20)).pack(pady=5)

        # Selección de Heurística (Cómo piensa la IA)
        ctk.CTkLabel(self.sidebar,
                     text="Heurística:",
                     font=("bold", 14)).pack(pady=10)

        self.h_var = ctk.StringVar(value="Manhattan")  # Variable que guarda la opción elegida

        ctk.CTkOptionMenu(self.sidebar,
                          values=["Fichas fuera", "Manhattan", "Weighted A*"],
                          variable=self.h_var).pack(pady=10)

        # Botón verde para ejecutar la Inteligencia Artificial
        self.btn_solve = ctk.CTkButton(self.sidebar,
                                       text="RESOLVER",
                                       height=50,
                                       font=ctk.CTkFont(size=14, weight="bold"),
                                       fg_color="#149900",
                                       command=self.run_ai)

        self.btn_solve.pack(pady=2, padx=20)

        # --- CONTENEDOR CENTRAL (Donde está el juego y la tabla) ---
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=0, pady=5)

        # Zona superior: Contiene la miniatura de la meta y el tablero de juego
        self.game_zone = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.game_zone.pack(pady=5)

        # Panel de "META" (la imagen pequeña de referencia)
        self.target_frame = ctk.CTkFrame(self.game_zone, fg_color="#1a1a1a", border_width=2, border_color="#444")
        self.target_frame.grid(row=0, column=0, padx=5, sticky="n")

        ctk.CTkLabel(self.target_frame, text="META", font=("Segoe UI", 12, "bold")).pack(pady=5)
        self.preview_label = tk.Label(self.target_frame, bg="#1a1a1a")  # Aquí se dibuja la miniatura

        self.preview_label.pack(padx=10, pady=10)

        # El cuadro principal donde estarán los botones del puzzle
        self.grid_frame = ctk.CTkFrame(self.game_zone, fg_color="#121212", border_width=3, border_color="#555")
        self.grid_frame.grid(row=0, column=1, padx=5)

        # Tabla de estadísticas (inferior)
        self.tree_frame = ctk.CTkFrame(self.main_container)
        self.tree_frame.pack(fill="x", side="bottom", pady=0, padx=15)

        cols = ("D", "H", "T", "M", "S")  # Identificadores de columnas
        self.tree = ttk.Treeview(self.tree_frame, columns=cols, show="headings", height=4)

        # Configuración de los nombres de las columnas de la tabla
        for c, h in zip(self.tree["columns"], ["Dimensión", "Heurística", "Tiempo (ms)", "Memoria (KB)", "Pasos"]):

            self.tree.heading(c, text=h)
            self.tree.column(c, width=100, anchor="center")

        self.tree.pack(fill="both", expand=True)

    # Cambia a la siguiente imagen disponible en la carpeta
    def cycle_image(self):

        # Incrementa el índice y vuelve a 0 si llega al final de la lista
        self.current_image_index = (self.current_image_index + 1) % len(self.image_files)

        self.load_local_image()  # Carga la nueva imagen
        self.generate_puzzle()  # Reinicia el puzzle con la nueva imagen

    # Carga el archivo JPG, lo recorta a cuadrado y lo escala
    def load_local_image(self):

        filename = self.image_files[self.current_image_index]

        # Verifica si el archivo realmente existe en la computadora
        if not os.path.exists(filename):
            messagebox.showerror("Error", f"No se encontró el archivo: {filename}")

            return

        try:
            img = Image.open(filename)
            w, h = img.size

            # Lógica para recortar la imagen y hacerla cuadrada (crop central)
            min_dim = min(w, h)
            left, top = (w - min_dim) / 2, (h - min_dim) / 2

            img = img.crop((left, top, left + min_dim, top + min_dim))

            # Redimensiona la imagen a un tamaño estándar (540x540)
            canvas_size = 540
            self.base_image = img.resize((canvas_size, canvas_size), Image.Resampling.LANCZOS)

            # Crea y muestra la miniatura (Preview) de 150x150
            preview_tk = ImageTk.PhotoImage(self.base_image.resize((150, 150)))

            self.preview_label.config(image=preview_tk)
            self.preview_label.image = preview_tk  # Evita que Python borre la imagen de memoria

            self.slice_image()  # Divide la imagen en trozos

        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar {filename}: {e}")

    # Divide la imagen base en N partes (3x3 = 9 partes, etc.)
    def slice_image(self):

        self.image_pieces = []
        p_size = self.base_image.size[0] // self.size  # Tamaño de cada pieza en píxeles

        for r in range(self.size):

            for c in range(self.size):

                left, top = c * p_size, r * p_size

                # Recorta el cuadrado correspondiente de la imagen original
                piece = self.base_image.crop((left, top, left + p_size, top + p_size))

                # Crea un pequeño borde oscuro alrededor de cada pieza
                bordered = Image.new('RGB', (p_size, p_size), "#333333")
                bordered.paste(piece, (1, 1))

                # Convierte la imagen a un formato que la interfaz gráfica entienda
                self.image_pieces.append(ImageTk.PhotoImage(bordered))

    # Cambia la dificultad del puzzle entre 3x3 y 4x4
    def change_size(self, val):

        self.size = 3 if val == "3x3 (8)" else 4
        self.slice_image()  # Vuelve a cortar la imagen en más o menos trozos
        self.generate_puzzle()  # Crea un nuevo tablero de ese tamaño

    # Crea el estado inicial del juego desordenándolo mediante movimientos válidos
    def generate_puzzle(self):

        # Borra los botones anteriores de la pantalla
        for widget in self.grid_frame.winfo_children(): widget.destroy()
        self.cells = {}  # Limpia el registro de celdas

        # --- CREACIÓN DEL ESTADO SOLUBLE ---
        # Crea una matriz ordenada (1, 2, 3...)
        state = np.arange(1, self.size ** 2 + 1).reshape(self.size, self.size)
        state[-1, -1] = 0  # El último número lo convierte en 0 (espacio vacío)

        # r y c guardan la posición actual del espacio vacío (esquina inferior derecha)
        r, c = self.size - 1, self.size - 1

        # Define cuántos movimientos al azar hará para desordenarlo
        moves = 40 if self.size == 3 else 80

        for _ in range(moves):

            # Elige una dirección al azar: arriba, abajo, izq, der
            dr, dc = random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])
            nr, nc = r + dr, c + dc  # Nueva posición tentativa

            # Si el movimiento no se sale del tablero, intercambia las piezas
            if 0 <= nr < self.size and 0 <= nc < self.size:

                state[r, c], state[nr, nc] = state[nr, nc], state[r, c]
                r, c = nr, nc  # Actualiza la posición del vacío

        self.current_state = state  # Guarda este desorden como el inicio del juego

        # --- DIBUJO DE LOS CANVASES (Celdas) EN LA INTERFAZ ---
        p_size = self.base_image.size[0] // self.size

        for r in range(self.size):

            for c in range(self.size):

                # Crea un lienzo (Canvas) para cada pieza
                canv = tk.Canvas(self.grid_frame, width=p_size - 1, height=p_size - 1,
                                 bg="#121212", highlightthickness=1, highlightbackground="#333")

                canv.grid(row=r, column=c)

                img_id = canv.create_image(0, 0, anchor="nw")  # Crea el objeto imagen dentro del lienzo

                self.cells[(r, c)] = (canv, img_id)  # Registra la celda para actualizarla luego

        self.update_display()  # Pone las imágenes correctas en los cuadros

    # Refresca las imágenes que se ven en el tablero según una matriz dada
    def update_display(self, state=None):

        target = state if state is not None else self.current_state

        for r in range(self.size):

            for c in range(self.size):

                val = target[r, c]  # Qué número hay en esta posición
                canv, img_canvas_id = self.cells[(r, c)]

                if val == 0:  # Si es el espacio vacío
                    canv.itemconfig(img_canvas_id, image="")  # No muestra imagen

                else:
                    # Busca el trozo de imagen correspondiente al número
                    img_tk = self.image_pieces[val - 1]
                    canv.itemconfig(img_canvas_id, image=img_tk)
                    canv.image_ref = img_tk  # Mantiene la referencia para que no desaparezca

    # Muestra una animación de la solución paso a paso
    def animate_path(self, path):

        def step(i):

            if i < len(path):

                # Actualiza el tablero con el paso actual de la lista de solución
                self.update_display(np.array(path[i]).reshape(self.size, self.size))

                # Espera 200 milisegundos y llama al siguiente paso
                self.after(200, lambda: step(i + 1))

            else:
                # Al terminar, vuelve a activar el botón de Resolver
                self.btn_solve.configure(state="normal")

        # Desactiva el botón durante la animación para evitar errores
        self.btn_solve.configure(state="disabled")

        step(0)  # Inicia la animación desde el paso cero

    # Ejecuta el algoritmo A* y procesa los resultados
    def run_ai(self):

        h = self.h_var.get()                # Obtiene la heurística elegida (ej: Manhattan)
        d_text = self.puzzle_type.get()     # Obtiene el tamaño actual
        d = "3x3" if "3x3" in d_text else "4x4"

        # Crea el objeto Solver pasándole el estado actual y la configuración
        solver = AStarPuzzleSolver(self.current_state, self.size, h)

        # Ejecuta la búsqueda. 'solve' devuelve éxito, el camino, tiempo y memoria.
        success, path, t, m = solver.solve()

        if success:
            # Inserta los datos de rendimiento en la tabla de la interfaz
            self.tree.insert("", 0, values=(d, h, f"{t:.1f}", f"{m:.1f}", len(path) - 1))

            # Inicia la animación de las piezas moviéndose solas
            self.animate_path(path)

        else:
            # Si no encontró solución, muestra una advertencia
            messagebox.showwarning("IA", "Insoluble o límite excedido.")