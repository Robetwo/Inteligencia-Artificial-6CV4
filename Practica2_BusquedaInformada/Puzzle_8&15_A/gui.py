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
        self.title("A* Photo Puzzle - Rob's Lab")
        self.geometry("800x600")

        self.size = 3
        self.current_state = None
        self.cells = {}
        self.image_pieces = []
        self.base_image = None

        # --- CONFIGURACIÓN DE ARCHIVOS LOCALES ---
        # Lista de nombres de archivos que deben estar en la misma carpeta
        self.image_files = ["1.jpg", "2.jpg"]
        self.current_image_index = 0

        self.setup_styles()
        self.setup_ui()
        self.load_local_image()  # Cargar desde archivo
        self.generate_puzzle()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b",
                        font=("Segoe UI", 11))
        style.configure("Treeview.Heading", background="#1f1f1f", foreground="white", font=("Segoe UI", 11, "bold"))
        style.map("Treeview", background=[('selected', '#3498db')])
        style.configure("Treeview", rowheight=30)

    def setup_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # Título en una sola línea con dos colores
        title_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        title_frame.pack(pady=20)
        ctk.CTkLabel(title_frame, text="PHOTO", font=ctk.CTkFont(size=28, weight="bold")).grid(row=0, column=0)
        ctk.CTkLabel(title_frame, text="IA", text_color="yellow", font=ctk.CTkFont(size=28, weight="bold")).grid(row=0,
                                                                                                                 column=1,
                                                                                                                 padx=5)

        ctk.CTkLabel(self.sidebar, text="Configuración:", font=("bold", 14)).pack(pady=10)
        self.puzzle_type = ctk.CTkSegmentedButton(self.sidebar, values=["3x3 (8)", "4x4 (15)"],
                                                  command=self.change_size)
        self.puzzle_type.set("3x3 (8)")
        self.puzzle_type.pack(padx=20, pady=10)

        ctk.CTkLabel(self.sidebar, text="Heurística:", font=("bold", 14)).pack(pady=10)
        self.h_var = ctk.StringVar(value="Manhattan")
        ctk.CTkOptionMenu(self.sidebar, values=["Fichas fuera", "Manhattan", "Personalizada"],
                          variable=self.h_var).pack(pady=10)

        # Botón Cambiar Imagen (Gris oscuro)
        self.btn_change_img = ctk.CTkButton(self.sidebar, text="CAMBIAR FOTO", height=45, fg_color="#34495e",
                                            command=self.cycle_image)
        self.btn_change_img.pack(pady=10, padx=20)

        # Botón Mezclar (Naranja)
        self.btn_random = ctk.CTkButton(self.sidebar, text="MEZCLAR", height=45, fg_color="#e67e22",
                                        command=self.generate_puzzle)
        self.btn_random.pack(pady=10, padx=20)

        # Botón Resolver (Verde)
        self.btn_solve = ctk.CTkButton(self.sidebar, text="RESOLVER", height=50, font=ctk.CTkFont(weight="bold"),
                                       fg_color="#149900", command=self.run_ai)
        self.btn_solve.pack(pady=50, padx=20)

        # --- CONTENEDOR CENTRAL ---
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=0, pady=5)

        # Frame para la zona de juego (Imagen Meta + Puzzle)
        self.game_zone = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.game_zone.pack(pady=5)

        # 1. IMAGEN OBJETIVO (Arriba a la izquierda del puzzle)
        self.target_frame = ctk.CTkFrame(self.game_zone, fg_color="#1a1a1a", border_width=2, border_color="#444")
        self.target_frame.grid(row=0, column=0, padx=5, sticky="n")

        ctk.CTkLabel(self.target_frame, text="META", font=("Segoe UI", 12, "bold")).pack(pady=5)
        self.preview_label = tk.Label(self.target_frame, bg="#1a1a1a")
        self.preview_label.pack(padx=10, pady=10)

        # 2. TABLERO DEL PUZZLE
        self.grid_frame = ctk.CTkFrame(self.game_zone, fg_color="#121212", border_width=3, border_color="#555")
        self.grid_frame.grid(row=0, column=1, padx=5)

        # --- TABLA DE RENDIMIENTO (Abajo) ---
        self.tree_frame = ctk.CTkFrame(self.main_container)
        self.tree_frame.pack(fill="x", side="bottom", pady=0)

        cols = ("H", "T", "M", "S")
        self.tree = ttk.Treeview(self.tree_frame, columns=cols, show="headings", height=4)
        for c, h in zip(self.tree["columns"], ["Heurística", "Tiempo (s)", "Memoria (KB)", "Pasos"]):
            self.tree.heading(c, text=h)
            self.tree.column(c, width=100, anchor="center")
        self.tree.pack(fill="both", expand=True)

    # ==========================================
    # LÓGICA DE ARCHIVOS LOCALES
    # ==========================================

    def cycle_image(self):
        self.current_image_index = (self.current_image_index + 1) % len(self.image_files)
        self.load_local_image()
        self.generate_puzzle()

    def load_local_image(self):
        """Carga la imagen desde el archivo local por nombre."""
        filename = self.image_files[self.current_image_index]

        if not os.path.exists(filename):
            messagebox.showerror("Error",
                                 f"No se encontró el archivo: {filename}\nAsegúrate de que esté en la misma carpeta.")
            return

        try:
            img = Image.open(filename)

            # Hacer cuadrada
            w, h = img.size
            min_dim = min(w, h)
            left, top = (w - min_dim) / 2, (h - min_dim) / 2
            img = img.crop((left, top, left + min_dim, top + min_dim))

            # Redimensionar
            canvas_size = 540
            self.base_image = img.resize((canvas_size, canvas_size), Image.Resampling.LANCZOS)

            # Preview
            preview_tk = ImageTk.PhotoImage(self.base_image.resize((150, 150)))
            self.preview_label.config(image=preview_tk)
            self.preview_label.image = preview_tk

            self.slice_image()
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar {filename}: {e}")

    def slice_image(self):
        self.image_pieces = []
        p_size = self.base_image.size[0] // self.size
        for r in range(self.size):
            for c in range(self.size):
                left, top = c * p_size, r * p_size
                piece = self.base_image.crop((left, top, left + p_size, top + p_size))

                # Borde decorativo
                bordered = Image.new('RGB', (p_size, p_size), "#333333")
                bordered.paste(piece, (1, 1))
                self.image_pieces.append(ImageTk.PhotoImage(bordered))

    # ==========================================
    # LÓGICA DE CONTROL
    # ==========================================

    def change_size(self, val):
        self.size = 3 if "3x3" in val else 4
        self.slice_image()
        self.generate_puzzle()

    def generate_puzzle(self):
        for widget in self.grid_frame.winfo_children(): widget.destroy()
        self.cells = {}

        nums = list(range(self.size ** 2))
        random.shuffle(nums)
        self.current_state = np.array(nums).reshape(self.size, self.size)

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
        target = state if state is not None else self.current_state
        for r in range(self.size):
            for c in range(self.size):
                val = target[r, c]
                canv, img_canvas_id = self.cells[(r, c)]
                if val == 0:
                    canv.itemconfig(img_canvas_id, image="")
                else:
                    img_tk = self.image_pieces[val - 1]
                    canv.itemconfig(img_canvas_id, image=img_tk)
                    canv.image_ref = img_tk

    def animate_path(self, path):
        def step(i):
            if i < len(path):
                self.update_display(np.array(path[i]).reshape(self.size, self.size))
                self.after(200, lambda: step(i + 1))
            else:
                self.btn_solve.configure(state="normal")

        self.btn_solve.configure(state="disabled")
        step(0)

    def run_ai(self):
        h = self.h_var.get()
        solver = AStarPuzzleSolver(self.current_state, self.size, h)
        success, path, t, m = solver.solve()
        if success:
            self.tree.insert("", 0, values=(h, f"{t:.4f}", f"{m:.1f}", len(path) - 1))
            self.animate_path(path)
        else:
            messagebox.showwarning("IA", "Insoluble o límite excedido.")