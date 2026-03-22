import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import random
from solvers import AStarSolver, SimulatedAnnealingSolver

class ModernSudokuApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        # --- CONFIGURACIÓN DE LA VENTANA ---
        self.title("Sudoku AI Solver - Comparativa de Algoritmos")
        self.geometry("700x650")

        # Estado inicial: Matriz de 9x9 llena de ceros
        self.current_board = np.zeros((9, 9), dtype=int)
        self.cells = {} # Diccionario para rastrear los widgets (etiquetas) de la cuadrícula
        
        self.setup_styles()
        self.setup_ui()
        self.generate_new_board()

    def setup_styles(self):
        """Define la estética de la tabla de resultados inferior."""
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", 
                        background="#2b2b2b", 
                        foreground="white", 
                        fieldbackground="#2b2b2b", 
                        borderwidth=0, 
                        font=("Segoe UI", 12))
        style.configure("Treeview.Heading", 
                        background="#1f1f1f", 
                        foreground="white", 
                        relief="flat", 
                        font=("Segoe UI", 14, "bold"))
        style.map("Treeview", background=[('selected', '#3498db')])

    def setup_ui(self):
        """Construye la interfaz: Barra lateral de control y Tablero central."""
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- PANEL LATERAL (SIDEBAR) ---
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # Títulos
        ctk.CTkLabel(self.sidebar, text="SUDOKU", font=ctk.CTkFont(size=32, weight="bold")).pack(pady=15)
        ctk.CTkLabel(self.sidebar, text="INTELIGENCIA ARTIFICIAL", text_color="yellow", 
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=0)

        # Selección de Dificultad
        ctk.CTkLabel(self.sidebar, text="Nivel de Dificultad:", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=20)
        self.lvl_btn = ctk.CTkSegmentedButton(self.sidebar, values=["Fácil", "Medio", "Difícil"], 
                                             command=self.generate_new_board)
        self.lvl_btn.set("Fácil")
        self.lvl_btn.pack(padx=20, pady=10)

        # Botón para refrescar el tablero
        self.btn_random = ctk.CTkButton(self.sidebar, text="NUEVO TABLERO", height=40,
                                        font=ctk.CTkFont(size=13, weight="bold"),
                                        fg_color="#0E6582", hover_color="#2c3e50",
                                        command=self.generate_new_board)
        self.btn_random.pack(pady=10, padx=20)

        # Selección de Algoritmo de IA
        ctk.CTkLabel(self.sidebar, text="Seleccionar Algoritmo:", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=20)
        self.algo_var = ctk.StringVar(value="Búsqueda A*")
        self.algo_menu = ctk.CTkOptionMenu(self.sidebar, 
                                           values=["Búsqueda A*", "Recocido Simulado"], 
                                           variable=self.algo_var)
        self.algo_menu.pack(pady=1)

        # Botón Ejecutar
        self.btn_solve = ctk.CTkButton(self.sidebar, text="RESOLVER", height=45, 
                                       font=ctk.CTkFont(size=14, weight="bold"),
                                       fg_color="#149900", hover_color="#219150", 
                                       command=self.run_ai)
        self.btn_solve.pack(pady=30, padx=20)

        # --- ÁREA DEL TABLERO (CENTRO) ---
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.board_frame = ctk.CTkFrame(self.main_container, fg_color="#121212", 
                                        border_width=3, border_color="#333")
        self.board_frame.pack(pady=5)

        # Generación de las 81 celdas (9x9)
        for r in range(9):
            for c in range(9):
                # Lógica visual: Colorear subcuadrículas 3x3 de forma alterna para facilitar lectura
                is_subgrid = (r // 3 + c // 3) % 2 == 0
                color = "#252525" if is_subgrid else "#1e1e1e"
                
                cell = tk.Label(self.board_frame, text="", width=4, height=2,
                                font=("Segoe UI", 18, "bold"), bg=color, fg="#ecf0f1",
                                highlightthickness=1, highlightbackground="#333")
                cell.grid(row=r, column=c, padx=1, pady=1)
                self.cells[(r, c)] = cell

        # --- TABLA DE MÉTRICAS (INFERIOR) ---
        self.tree_frame = ctk.CTkFrame(self.main_container, height=150)
        self.tree_frame.pack(fill="x", side="bottom", pady=10)

        cols = ("Algoritmo", "Tiempo (s)", "Memoria (KB)", "Status")
        self.tree = ttk.Treeview(self.tree_frame, columns=cols, show="headings", height=5)
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="center")
        self.tree.pack(fill="both", expand=True)

    def generate_new_board(self, *args):
        """Crea un Sudoku válido y oculta números según la dificultad elegida."""
        # Generación matemática de un tablero base válido
        base = [[(i * 3 + i // 3 + j) % 9 + 1 for j in range(9)] for i in range(9)]
        random.shuffle(base)
        self.current_board = np.array(base)

        # Definir cuántas pistas quitar (a más vacías, más difícil)
        vacias = {"Fácil": 20, "Medio": 35, "Difícil": 45}[self.lvl_btn.get()]
        idx = [(r, c) for r in range(9) for c in range(9)]
        
        # Seleccionamos posiciones aleatorias para poner en 0 (vacío)
        for r, c in random.sample(idx, vacias):
            self.current_board[r, c] = 0
        self.update_display()

    def update_display(self, board=None):
        """Actualiza el texto y color de las celdas en la pantalla."""
        target = board if board is not None else self.current_board
        for r in range(9):
            for c in range(9):
                val = target[r, c]
                # Si el número fue puesto por la IA (board no es None), lo pintamos de azul
                color = "#3498db" if (board is not None and self.current_board[r, c] == 0) else "white"
                
                self.cells[(r, c)].config(
                    text=str(val) if val != 0 else "",
                    fg=color
                )

    def animate(self, solved_board, delay=30):
        """Muestra la solución paso a paso para fines didácticos en la exposición."""
        # Identificamos qué celdas estaban vacías originalmente
        empty = [(r, c) for r in range(9) for c in range(9) if self.current_board[r, c] == 0]

        def step(i):
            if i < len(empty):
                r, c = empty[i]
                # Pintamos el número resuelto en verde
                self.cells[(r, c)].config(text=str(solved_board[r, c]), fg="#2ecc71")
                # Llamada recursiva con retardo para crear el efecto de animación
                self.after(delay, lambda: step(i + 1))
            else:
                self.btn_solve.configure(state="normal")

        self.btn_solve.configure(state="disabled") # Bloquear botón mientras anima
        step(0)

    def run_ai(self):
        """Conecta la GUI con los algoritmos de IA en solvers.py."""
        algo_name = self.algo_var.get()
        
        # Selección de estrategia de resolución
        if "A*" in algo_name:
            # El solver A* usa búsqueda determinística (Backtracking optimizado)
            solver = AStarSolver(self.current_board)
        else:
            # El Recocido Simulado usa una metaheurística probabilística
            solver = SimulatedAnnealingSolver(self.current_board)
        
        # Ejecución y captura de métricas (Tiempo y Memoria RAM)
        res = solver.get_metrics(solver.solve)
        
        status = "Éxito" if res["success"] else "Fallo"
        # Insertar datos en la tabla comparativa
        self.tree.insert("", 0, values=(algo_name, f"{res['time']:.4f}", f"{res['memory']:.1f}", status))
        
        if res["success"]:
            self.animate(res["board"]) # Iniciar animación visual
        else:
            messagebox.showwarning("IA", "El algoritmo no pudo encontrar una solución óptima en este intento.")
