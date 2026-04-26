import customtkinter as ctk
from tkinter import messagebox
import time
import tracemalloc
import math
from models import TicTacToe4x4
from algorithms import Agente

# Configuración global de la apariencia moderna
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class GameGUI:

    def __init__(self, root):
        self.root = root
        self.root.title("Gato 4x4 - IA Minimax")
        self.root.geometry("850x570")  # Ligero ajuste de altura para la tabla
        self.root.resizable(False, False)

        self.model = TicTacToe4x4()
        self.agent = Agente(profundidad_maxima=2)

        self.buttons = [[None for _ in range(4)] for _ in range(4)]
        self.use_alpha_beta = ctk.BooleanVar(value=True)

        self.setup_ui()

    def setup_ui(self):
        # Contenedor principal transparente
        main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        main_frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)

        # --- Panel Izquierdo: Tablero ---
        board_frame = ctk.CTkFrame(main_frame, corner_radius=15)
        board_frame.pack(side=ctk.LEFT, padx=(0, 20), pady=10)

        for r in range(4):
            for c in range(4):
                btn = ctk.CTkButton(
                    board_frame,
                    text="",
                    width=90,
                    height=90,
                    corner_radius=10,
                    font=ctk.CTkFont(size=40, weight="bold"),
                    fg_color="#313244",
                    hover_color="#45475a",
                    command=lambda row=r, col=c: self.player_click(row, col)
                )
                btn.grid(row=r, column=c, padx=8, pady=8)
                self.buttons[r][c] = btn

        # --- Panel Derecho: Controles y Métricas ---
        side_panel = ctk.CTkFrame(main_frame, width=320, corner_radius=15)
        side_panel.pack(side=ctk.RIGHT, fill=ctk.Y, pady=10)
        side_panel.pack_propagate(False)

        inner_panel = ctk.CTkFrame(side_panel, fg_color="transparent")
        inner_panel.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)

        # Sección: Configuración
        ctk.CTkLabel(inner_panel,
                     text="Configuración",
                     text_color="yellow",
                     font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(0, 15))

        ctk.CTkRadioButton(
            inner_panel, text="Minimax", variable=self.use_alpha_beta, value=False,
            font=ctk.CTkFont(size=14), fg_color="#f38ba8", hover_color="#f38ba8"
        ).pack(anchor="w", pady=8)

        ctk.CTkRadioButton(
            inner_panel, text="Minimax + Alfa-Beta", variable=self.use_alpha_beta, value=True,
            font=ctk.CTkFont(size=14), fg_color="#89b4fa", hover_color="#89b4fa"
        ).pack(anchor="w", pady=8)

        # Divisor visual
        ctk.CTkFrame(inner_panel, height=2, fg_color="#45475a").pack(fill=ctk.X, pady=20)

        # Sección: Rendimiento (Formato Tabla)
        ctk.CTkLabel(inner_panel,
                     text="Rendimiento",
                     text_color="aqua",
                     font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(0, 10))

        # Contenedor de la tabla con fondo ligeramente más oscuro para contrastar
        table_frame = ctk.CTkFrame(inner_panel, fg_color="#181825", corner_radius=10)
        table_frame.pack(fill=ctk.X, pady=5)

        # Configurar columnas de la tabla para que se expandan equitativamente
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_columnconfigure(1, weight=1)

        # Encabezados de la Tabla
        ctk.CTkLabel(table_frame, text="Métrica", font=ctk.CTkFont(size=14, weight="bold"), text_color="#a6adc8").grid(
            row=0, column=0, padx=15, pady=(10, 5), sticky="w")
        ctk.CTkLabel(table_frame, text="Valor", font=ctk.CTkFont(size=14, weight="bold"), text_color="#a6adc8").grid(
            row=0, column=1, padx=15, pady=(10, 5), sticky="e")

        # Divisor interno de la tabla
        ctk.CTkFrame(table_frame, height=1, fg_color="#313244").grid(row=1, column=0, columnspan=2, sticky="ew",
                                                                     padx=10, pady=(0, 5))

        # Fila 1: Nodos
        ctk.CTkLabel(table_frame, text="Nodos", font=ctk.CTkFont(size=13)).grid(row=2, column=0, padx=15, pady=5,
                                                                                sticky="w")
        self.val_nodes = ctk.CTkLabel(table_frame, text="0", font=ctk.CTkFont(size=13, weight="bold"),
                                      text_color="#f9e2af")  # Amarillo
        self.val_nodes.grid(row=2, column=1, padx=15, pady=5, sticky="e")

        # Fila 2: Tiempo
        ctk.CTkLabel(table_frame, text="Tiempo", font=ctk.CTkFont(size=13)).grid(row=3, column=0, padx=15, pady=5,
                                                                                 sticky="w")
        self.val_time = ctk.CTkLabel(table_frame, text="0.000 s", font=ctk.CTkFont(size=13, weight="bold"),
                                     text_color="#a6e3a1")  # Verde
        self.val_time.grid(row=3, column=1, padx=15, pady=5, sticky="e")

        # Fila 3: Memoria
        ctk.CTkLabel(table_frame, text="Memoria Pico", font=ctk.CTkFont(size=13)).grid(row=4, column=0, padx=15,
                                                                                       pady=(5, 10), sticky="w")
        self.val_mem = ctk.CTkLabel(table_frame, text="0.00 KB", font=ctk.CTkFont(size=13, weight="bold"),
                                    text_color="#89dceb")  # Cyan
        self.val_mem.grid(row=4, column=1, padx=15, pady=(5, 10), sticky="e")

        # Botón de Reinicio
        ctk.CTkButton(
            inner_panel, text="Reiniciar Juego",
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#f38ba8", text_color="#11111b", hover_color="#eba0ac",
            command=self.reset_game
        ).pack(side=ctk.BOTTOM, fill=ctk.X, pady=(20, 0))

    def player_click(self, r, c):
        if self.model.board[r][c] == ' ' and not self.model.is_game_over():
            self.model.make_move(r, c, 'X')
            self.update_board_ui()

            if not self.check_game_end():
                self.root.update()
                self.ai_move()

    def ai_move(self):
        self.agent.nodes_explored = 0
        best_move = None

        tracemalloc.start()
        start_time = time.perf_counter()

        if self.use_alpha_beta.get():
            _, best_move = self.agent.minimax_alpha_beta(self.model, self.agent.profundidad_maxima, -math.inf, math.inf, True)
        else:
            _, best_move = self.agent.minimax(self.model, self.agent.profundidad_maxima, True)

        end_time = time.perf_counter()
        _, peak_memory = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # Actualizar solo los valores de la tabla
        self.val_nodes.configure(text=f"{self.agent.nodes_explored:,}")
        self.val_time.configure(text=f"{end_time - start_time:.3f} s")
        self.val_mem.configure(text=f"{peak_memory / 1024:.2f} KB")

        if best_move:
            self.model.make_move(best_move[0], best_move[1], 'O')
            self.update_board_ui()
            self.check_game_end()

    def update_board_ui(self):
        for r in range(4):
            for c in range(4):
                val = self.model.board[r][c]
                if val == 'X':
                    self.buttons[r][c].configure(text="X", text_color="#f38ba8")
                elif val == 'O':
                    self.buttons[r][c].configure(text="O", text_color="#89b4fa")
                else:
                    self.buttons[r][c].configure(text="")

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
        # Resetear los valores de la tabla
        self.val_nodes.configure(text="0")
        self.val_time.configure(text="0.000 s")
        self.val_mem.configure(text="0.00 KB")