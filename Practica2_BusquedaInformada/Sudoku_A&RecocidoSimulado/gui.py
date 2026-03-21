import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import random
from solvers import AStarSolver, SimulatedAnnealingSolver


class ModernSudokuApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sudoku AI Solver")
        self.geometry("700x650")

        self.current_board = np.zeros((9, 9), dtype=int)
        self.cells = {}
        self.setup_styles()
        self.setup_ui()
        self.generate_new_board()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b", borderwidth=0, font=("Segoe UI", 12))
        style.configure("Treeview.Heading", background="#1f1f1f", foreground="white", relief="flat", font=("Segoe UI", 14, "bold"))
        style.map("Treeview", background=[('selected', '#3498db')])

    def setup_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(self.sidebar, text="SUDOKU", font=ctk.CTkFont(size=32, weight="bold")).pack(pady=15)
        ctk.CTkLabel(self.sidebar, text="IA", text_color="yellow", font=ctk.CTkFont(size=26, weight="bold")).pack(
            pady=0)
        ctk.CTkLabel(self.sidebar, text="", font=ctk.CTkFont(size=20)).pack(pady=15)

        ctk.CTkLabel(self.sidebar, text="Nivel de Dificultad:", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)
        self.lvl_btn = ctk.CTkSegmentedButton(self.sidebar, values=["Fácil", "Medio", "Difícil"],
                                              command=self.generate_new_board)
        self.lvl_btn.set("Fácil")
        self.lvl_btn.pack(padx=20, pady=10)

        self.btn_random = ctk.CTkButton(self.sidebar, text="NUEVO TABLERO", height=40,
                                        font=ctk.CTkFont(size=13, weight="bold"),
                                        fg_color="#0E6582", hover_color="#2c3e50",
                                        command=self.generate_new_board)
        self.btn_random.pack(pady=10, padx=20)

        ctk.CTkLabel(self.sidebar, text="", font=ctk.CTkFont(size=20)).pack(pady=15)

        ctk.CTkLabel(self.sidebar, text="Algoritmo:", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)
        self.algo_var = ctk.StringVar(value="Búsqueda A*")
        self.algo_menu = ctk.CTkOptionMenu(self.sidebar, values=["Búsqueda A*", "Recocido Simulado"], variable=self.algo_var)
        self.algo_menu.pack(pady=1)

        # Botón Resolver
        self.btn_solve = ctk.CTkButton(self.sidebar, text="RESOLVER", height=40, font=ctk.CTkFont(size=14, weight="bold"),
                                       fg_color="#149900", hover_color="#219150", command=self.run_ai)
        self.btn_solve.pack(pady=20, padx=20)

        # --- TABLERO CENTRAL ---
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=1, pady=0)

        self.board_frame = ctk.CTkFrame(self.main_container, fg_color="#121212", border_width=3, border_color="#333")
        self.board_frame.pack(pady=1)

        for r in range(9):
            for c in range(9):
                is_subgrid = (r // 3 + c // 3) % 2 == 0
                color = "#252525" if is_subgrid else "#1e1e1e"
                cell = tk.Label(self.board_frame, text="", width=4, height=2,
                                font=("Segoe UI", 18, "bold"), bg=color, fg="#ecf0f1",
                                highlightthickness=1, highlightbackground="#333")
                cell.grid(row=r, column=c, padx=1, pady=1)
                self.cells[(r, c)] = cell

        self.tree_frame = ctk.CTkFrame(self.main_container, height=150)
        self.tree_frame.pack(fill="x", side="bottom", pady=10)

        cols = ("Algoritmo", "Tiempo (s)", "Memoria (KB)", "Status")
        self.tree = ttk.Treeview(self.tree_frame, columns=cols, show="headings", height=5)
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="center")
        self.tree.pack(fill="both", expand=True)

    def generate_new_board(self, *args):
        # Lógica de generación de tablero
        base = [[(i * 3 + i // 3 + j) % 9 + 1 for j in range(9)] for i in range(9)]
        random.shuffle(base)
        self.current_board = np.array(base)

        vacias = {"Fácil": 20, "Medio": 35, "Difícil": 45}[self.lvl_btn.get()]
        idx = [(r, c) for r in range(9) for c in range(9)]
        for r, c in random.sample(idx, vacias):
            self.current_board[r, c] = 0
        self.update_display()

    def update_display(self, board=None):
        target = board if board is not None else self.current_board
        for r in range(9):
            for c in range(9):
                val = target[r, c]
                self.cells[(r, c)].config(
                    text=str(val) if val != 0 else "",
                    fg="#3498db" if (board is not None and self.current_board[r, c] == 0) else "white"
                )

    def animate(self, solved_board, delay=30):
        empty = [(r, c) for r in range(9) for c in range(9) if self.current_board[r, c] == 0]

        def step(i):
            if i < len(empty):
                r, c = empty[i]
                self.cells[(r, c)].config(text=str(solved_board[r, c]), fg="#2ecc71")
                self.after(delay, lambda: step(i + 1))
            else:
                self.btn_solve.configure(state="normal")

        self.btn_solve.configure(state="disabled")
        step(0)

    def run_ai(self):
        algo_name = self.algo_var.get()
        solver = AStarSolver(self.current_board) if "A*" in algo_name else SimulatedAnnealingSolver(self.current_board)
        res = solver.get_metrics(solver.solve)
        status = "Éxito" if res["success"] else "Fallo"
        self.tree.insert("", 0, values=(algo_name, f"{res['time']:.4f}", f"{res['memory']:.1f}", status))
        if res["success"]:
            self.animate(res["board"])
        else:
            messagebox.showwarning("IA", "No se encontró solución en el tiempo límite.")