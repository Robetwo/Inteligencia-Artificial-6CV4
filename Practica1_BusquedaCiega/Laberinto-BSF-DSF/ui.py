import tkinter as tk
from tkinter import ttk, messagebox
from maze import Maze
from algorithms import Pathfinder


class MazeSolverApp:
    def __init__(self, root):
        # 1. CONFIGURACIÓN DE LA VENTANA PRINCIPAL
        self.root = root
        self.root.title("Laberinto por BFS y DFS")  # Título de la ventana
        self.root.geometry("900x650")  # Ancho x Alto inicial
        self.root.configure(bg="#121111")  # Color de fondo (Gris muy oscuro)

        # 2. VARIABLES DE CONTROL DE LA INTERFAZ
        # Estas variables están conectadas a los menús desplegables. Si el menú cambia, la variable cambia automáticamente.
        self.grid_size = tk.IntVar(value=20)  # Guarda el tamaño de la cuadrícula (por defecto 20x20)
        self.maze_type = tk.StringVar(value="Aleatorio (Baja Complejidad)")  # Tipo de generación
        self.algorithm = tk.StringVar(value="BFS")  # Algoritmo elegido

        # 3. ESTADO INTERNO DEL PROGRAMA
        self.maze = None  # Aquí guardaremos el objeto del laberinto lógico
        self.canvas_size = 600  # Tamaño fijo del área de dibujo en píxeles (600x600)
        self.rects = {}  # Diccionario: guarda {coordenada (x,y): ID_del_rectángulo_dibujado}
        self.is_animating = False  # Bandera para bloquear botones mientras hay una animación en curso

        # 4. INICIALIZACIÓN
        self.setup_ui()  # Construye todos los elementos visuales
        self.generate_maze()  # Dibuja el primer laberinto al abrir la app

    def setup_ui(self):
        # ==========================================
        # PANEL IZQUIERDO: CONTROLES Y MÉTRICAS
        # ==========================================
        # Creamos un 'Frame' (contenedor) para los controles a la izquierda
        control_frame = tk.Frame(self.root, width=300, bg="#141313", padx=20, pady=20)
        control_frame.pack(side=tk.LEFT, fill=tk.Y)  # fill=tk.Y hace que ocupe toda la altura

        # Título principal del panel de control
        tk.Label(control_frame, text="Configuración \ndel\nLaberinto", font=("Rockwell", 20, "bold"), fg="#20DF96",
                 bg="#141313").pack(pady=(0, 15))

        # --- SELECCIÓN DE TAMAÑO ---
        tk.Label(control_frame, text="Tamaño:", fg="#3EABEF", font=("Rockwell", 12, "bold"), bg="#141313").pack(
            anchor=tk.W)
        # Combobox (menú desplegable) conectado a self.grid_size
        ttk.Combobox(control_frame, textvariable=self.grid_size, values=[10, 20, 50], font=("Arial", 11),
                     state="readonly").pack(fill=tk.X, pady=(0, 15))

        # --- SELECCIÓN DE TIPO DE LABERINTO ---
        tk.Label(control_frame, text="Tipo:", fg="#EC3713", font=("Rockwell", 12, "bold"), bg="#141313").pack(
            anchor=tk.W)
        ttk.Combobox(control_frame, textvariable=self.maze_type, state="readonly",
                     values=["Aleatorio (Baja Complejidad)", "Aleatorio (Alta Complejidad)", "Predefinido"],
                     font=("Arial", 10)).pack(
            fill=tk.X, pady=(0, 15))

        # --- BOTÓN PARA GENERAR LABERINTO ---
        # command=self.generate_maze asocia el clic a esa función
        tk.Button(control_frame, text="Generar Laberinto", font=("Furura", 12), command=self.generate_maze,
                  bg="#4CAF50", fg="white").pack(
            fill=tk.X, pady=(0, 25))

        # --- SELECCIÓN DE ALGORITMO ---
        tk.Label(control_frame, text="Algoritmo:", fg="#C112C4", font=("Rockwell", 12, "bold"), bg="#141313").pack(
            anchor=tk.W)
        ttk.Combobox(control_frame, textvariable=self.algorithm, values=["BFS", "DFS"], font=("Arial", 11),
                     state="readonly").pack(
            fill=tk.X, pady=(0, 15))

        # --- BOTÓN PARA RESOLVER ---
        tk.Button(control_frame, text="Resolver y Animar", font=("Furura", 12), command=self.solve_maze, bg="#2196F3",
                  fg="white").pack(
            fill=tk.X, pady=(0, 25))

        # --- SECCIÓN DE RESULTADOS (MÉTRICAS) ---
        tk.Label(control_frame, text="Métricas:", fg="#FFFFFF", font=("Arial", 12, "bold"), bg="#141313").pack(
            anchor=tk.W, pady=(10, 5))
        # Guardamos estas etiquetas en variables (self.lbl_...) para poder cambiar su texto después de resolver
        self.lbl_time = tk.Label(control_frame, text="Tiempo: 0.0000 ms", fg="#FFFFFF", font=("Arial", 10),
                                 bg="#141313")
        self.lbl_time.pack(anchor=tk.W)
        self.lbl_memory = tk.Label(control_frame, text="Memoria Pico: 0 KB", fg="#FFFFFF", font=("Arial", 10),
                                   bg="#141313")
        self.lbl_memory.pack(anchor=tk.W)
        self.lbl_path = tk.Label(control_frame, text="Longitud del camino: 0 pasos", fg="#FFFFFF", font=("Arial", 10),
                                 bg="#141313")
        self.lbl_path.pack(anchor=tk.W)

        # ==========================================
        # PANEL DERECHO: EL LIENZO (CANVAS) PARA DIBUJAR
        # ==========================================
        # Frame contenedor para centrar el área de dibujo
        canvas_frame = tk.Frame(self.root, bg="#1F1D1D")
        canvas_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=20, pady=20)
        # El Canvas es donde realmente pintaremos los cuadritos del laberinto
        self.canvas = tk.Canvas(canvas_frame, width=self.canvas_size, height=self.canvas_size, bg="white",
                                highlightthickness=1, highlightbackground="black")
        self.canvas.pack(anchor=tk.CENTER, expand=True)

    def generate_maze(self):
        # Si hay una animación corriendo, ignoramos el clic en el botón
        if self.is_animating: return

        # Obtenemos los valores actuales de los menús desplegables
        size = self.grid_size.get()
        m_type = self.maze_type.get()
        # Creamos una nueva instancia de la clase lógica Maze
        self.maze = Maze(size)

        # Llamamos al método de generación correspondiente según el texto del combobox
        if "Baja" in m_type:
            self.maze.generate_random("low")
        elif "Alta" in m_type:
            self.maze.generate_random("high")
        else:
            self.maze.generate_predefined()

        # Una vez generado el laberinto lógico, lo dibujamos en pantalla
        self.draw_grid()
        self.reset_metrics()  # Ponemos el tiempo y memoria a cero

    def draw_grid(self):
        # Limpiamos el lienzo de dibujos anteriores y vaciamos el diccionario de IDs
        self.canvas.delete("all")
        self.rects.clear()

        # Calculamos cuánto debe medir cada cuadrito para encajar en los 600px
        cell_w = self.canvas_size / self.maze.size
        cell_h = self.canvas_size / self.maze.size

        # Recorremos cada fila (r) y columna (c) de la matriz lógica
        for r in range(self.maze.size):
            for c in range(self.maze.size):
                color = "white"  # Por defecto asumimos que es un pasillo vacío

                # Determinamos el color según lo que haya en self.maze.grid
                if self.maze.grid[r][c] == 1:
                    color = "#333333"  # Muro (Gris oscuro)
                elif (r, c) == self.maze.start_node:
                    color = "#4CAF50"  # Nodo de Inicio (Verde)
                elif (r, c) == self.maze.end_node:
                    color = "#F44336"  # Nodo Final (Rojo)

                # Dibujamos el rectángulo matemático en el Canvas
                # Las coordenadas son (x1, y1) hasta (x2, y2)
                rect = self.canvas.create_rectangle(c * cell_w, r * cell_h, (c + 1) * cell_w, (r + 1) * cell_h,
                                                    fill=color, outline="#dddddd")
                # Guardamos la referencia visual (ID) vinculada a su coordenada (r, c)
                self.rects[(r, c)] = rect

    def solve_maze(self):
        if self.is_animating: return
        self.draw_grid()  # Limpiar colores anteriores de una solución previa

        # Instanciamos el solucionador y le pasamos nuestro laberinto actual
        pathfinder = Pathfinder(self.maze)
        # Obtenemos el diccionario con tiempo, memoria, camino, etc.
        results = pathfinder.solve(self.algorithm.get())

        # Actualizamos las etiquetas de la interfaz con los datos formateados
        self.lbl_time.config(text=f"Tiempo: {results['time_ms']:.4f} ms")
        self.lbl_memory.config(text=f"Memoria Pico: {results['peak_mem_kib']:.2f} KB")
        # Sumamos 1 al largo del camino para contar la casilla de inicio
        self.lbl_path.config(text=f"Longitud del camino: {len(results['path']) + 1 if results['found'] else 0} pasos")

        # Si el algoritmo dice que no encontró salida, mostramos alerta y salimos
        if not results['found']:
            messagebox.showinfo("Resultado", "No se encontró camino.")
            return

        # Bloqueamos los botones
        self.is_animating = True
        # Calculamos la velocidad de animación (más rápido si el mapa es grande)
        speed = 50 if self.maze.size == 10 else (10 if self.maze.size == 20 else 1)
        # Iniciamos el proceso recursivo de pintar cuadritos
        self.animate_search(results['visited_order'], results['path'], speed)

    def animate_search(self, visited, path, speed):
        # Función interna recursiva para pintar los visitados (búsqueda)
        def draw_visited(index):
            if index < len(visited):
                # Extrae la coordenada y busca su ID visual en el diccionario rects
                r, c = visited[index]
                self.canvas.itemconfig(self.rects[(r, c)], fill="#add8e6")  # Pinta Celeste
                # Programa la siguiente iteración después de 'speed' milisegundos sin congelar la app
                self.root.after(speed, draw_visited, index + 1)
            else:
                # Si ya pintó todos los visitados, pasa a pintar la ruta
                draw_path(0)

        # Función interna recursiva para pintar el camino final
        def draw_path(index):
            if index < len(path):
                r, c = path[index]
                self.canvas.itemconfig(self.rects[(r, c)], fill="#FFD700")  # Pinta Dorado
                # Es ligeramente más lenta (speed + 10) para darle énfasis al camino correcto
                self.root.after(speed + 10, draw_path, index + 1)
            else:
                # Al terminar la última casilla, libera los botones
                self.is_animating = False

        # Inicia la cadena llamando al primer elemento de visitados
        draw_visited(0)

    def reset_metrics(self):
        # Función auxiliar para restablecer visualmente los textos
        self.lbl_time.config(text="Tiempo: 0.0000 ms")
        self.lbl_memory.config(text="Memoria Pico: 0 KB")
        self.lbl_path.config(text="Longitud del camino: 0 pasos")
