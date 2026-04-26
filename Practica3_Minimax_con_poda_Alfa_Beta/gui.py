import math
import tkinter as tk
from tkinter import messagebox
import time
import tracemalloc
from models import TicTacToe4x4
from algorithms import Agent

# Paleta Modo Oscuro
BG_COLOR = "#1e1e2e"
FG_COLOR = "#cdd6f4"
BTN_BG = "#313244"
BTN_ACTIVE = "#45475a"
X_COLOR = "#f38ba8"
O_COLOR = "#89b4fa"
PANEL_BG = "#181825"


class GameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Gato 4x4 - AI Agent")
        self.root.geometry("800x550")
        self.root.configure(bg=BG_COLOR)

        self.model = TicTacToe4x4()
        self.agent = Agent(max_depth=4)  # Límite para evitar tiempos excesivos en 4x4

        self.buttons = [[None for _ in range(4)] for _ in range(4)]
        self.use_alpha_beta = tk.BooleanVar(value=True)

        self.setup_ui()

    def setup_ui(self):
        main_frame = tk.Frame(self.root, bg=BG_COLOR)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Tablero 4x4 (Izquierda)
        board_frame = tk.Frame(main_frame, bg=BG_COLOR)
        board_frame.pack(side=tk.LEFT, padx=20)

        for r in range(4):
            for c in range(4):
                btn = tk.Button(board_frame, text=" ", font=('Helvetica', 28, 'bold'), width=4, height=2,
                                bg=BTN_BG, fg=FG_COLOR, activebackground=BTN_ACTIVE, bd=0,
                                command=lambda row=r, col=c: self.player_click(row, col))
                btn.grid(row=r, column=c, padx=5, pady=5)
                self.buttons[r][c] = btn

        # Panel Lateral (Derecha)
        side_panel = tk.Frame(main_frame, bg=PANEL_BG, width=250, padx=20, pady=20)
        side_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=10)
        side_panel.pack_propagate(False)

        tk.Label(side_panel, text="Configuración IA", bg=PANEL_BG, fg=FG_COLOR, font=('Helvetica', 14, 'bold')).pack(
            pady=(0, 15))

        tk.Radiobutton(side_panel, text="Minimax Puro", variable=self.use_alpha_beta, value=False,
                       bg=PANEL_BG, fg=FG_COLOR, selectcolor=BTN_BG, activebackground=PANEL_BG,
                       activeforeground=FG_COLOR, font=('Helvetica', 11)).pack(anchor=tk.W, pady=5)
        tk.Radiobutton(side_panel, text="Minimax + Alfa-Beta", variable=self.use_alpha_beta, value=True,
                       bg=PANEL_BG, fg=FG_COLOR, selectcolor=BTN_BG, activebackground=PANEL_BG,
                       activeforeground=FG_COLOR, font=('Helvetica', 11)).pack(anchor=tk.W, pady=5)

        tk.Frame(side_panel, height=2, bg=BTN_ACTIVE).pack(fill=tk.X, pady=20)  # Divisor

        tk.Label(side_panel, text="Rendimiento", bg=PANEL_BG, fg=FG_COLOR, font=('Helvetica', 14, 'bold')).pack(
            pady=(0, 15))

        self.lbl_nodes = tk.Label(side_panel, text="Nodos Explorados: 0", bg=PANEL_BG, fg=FG_COLOR,
                                  font=('Helvetica', 10), anchor="w")
        self.lbl_nodes.pack(fill=tk.X, pady=5)

        self.lbl_time = tk.Label(side_panel, text="Tiempo: 0.000 s", bg=PANEL_BG, fg=FG_COLOR, font=('Helvetica', 10),
                                 anchor="w")
        self.lbl_time.pack(fill=tk.X, pady=5)

        self.lbl_mem = tk.Label(side_panel, text="Memoria Pico: 0 KB", bg=PANEL_BG, fg=FG_COLOR, font=('Helvetica', 10),
                                anchor="w")
        self.lbl_mem.pack(fill=tk.X, pady=5)

        tk.Button(side_panel, text="Reiniciar Juego", bg="#f38ba8", fg="#11111b", font=('Helvetica', 12, 'bold'), bd=0,
                  command=self.reset_game).pack(side=tk.BOTTOM, fill=tk.X, pady=20)

    def player_click(self, r, c):
        if self.model.board[r][c] == ' ' and not self.model.is_game_over():
            # Movimiento del humano
            self.model.make_move(r, c, 'X')
            self.update_board_ui()

            if not self.check_game_end():
                self.root.update()  # Actualizar UI antes de que la IA piense
                self.ai_move()

    def ai_move(self):
        self.agent.nodes_explored = 0
        best_move = None

        # Medición de Rendimiento
        tracemalloc.start()
        start_time = time.perf_counter()

        if self.use_alpha_beta.get():
            _, best_move = self.agent.minimax_alpha_beta(self.model, self.agent.max_depth, -math.inf, math.inf, True)
        else:
            _, best_move = self.agent.minimax(self.model, self.agent.max_depth, True)

        end_time = time.perf_counter()
        _, peak_memory = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # Actualizar métricas
        self.lbl_nodes.config(text=f"Nodos Explorados: {self.agent.nodes_explored}")
        self.lbl_time.config(text=f"Tiempo: {end_time - start_time:.3f} s")
        self.lbl_mem.config(text=f"Memoria Pico: {peak_memory / 1024:.2f} KB")

        if best_move:
            self.model.make_move(best_move[0], best_move[1], 'O')
            self.update_board_ui()
            self.check_game_end()

    def update_board_ui(self):
        for r in range(4):
            for c in range(4):
                val = self.model.board[r][c]
                self.buttons[r][c].config(text=val)
                if val == 'X':
                    self.buttons[r][c].config(fg=X_COLOR)
                elif val == 'O':
                    self.buttons[r][c].config(fg=O_COLOR)

    def check_game_end(self):
        winner = self.model.check_winner()
        if winner:
            messagebox.showinfo("Fin del Juego", f"¡El jugador {winner} ha ganado!")
            return True
        elif len(self.model.get_available_moves()) == 0:
            messagebox.showinfo("Fin del Juego", "¡Es un empate!")
            return True
        return False

    def reset_game(self):
        self.model = TicTacToe4x4()
        self.update_board_ui()
        self.lbl_nodes.config(text="Nodos Explorados: 0")
        self.lbl_time.config(text="Tiempo: 0.000 s")
        self.lbl_mem.config(text="Memoria Pico: 0 KB")