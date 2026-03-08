import tkinter as tk
from tkinter import ttk, messagebox
import time
from PIL import Image, ImageTk  # Librería para manejar imágenes
from modelo import ProblemaPuzzle8
from algoritmos import BuscadorAlgoritmos


class InterfazPuzzle:
    def __init__(self, root):
        self.root = root
        self.root.title("IA - Puzzle de Imágenes")
        self.root.geometry("600x550")
        self.root.configure(bg="#2c3e50")

        self.canvas_size = 300
        self.tile_size = self.canvas_size // 3
        self.is_animating = False

        # --- GESTIÓN DE IMÁGENES ---
        # Asegúrate de tener estas imágenes en tu carpeta, o cambia los nombres aquí
        self.catalogo_imagenes = [
            {"nombre": "Snoopy enojado", "ruta": "1.jpg"},
            {"nombre": "Esnupi mimido", "ruta": "2.jpg"},
            {"nombre": "Perro Guacho", "ruta": "3.jpg"},
            {"nombre": "Perrito Feli", "ruta": "4.jpg"},
            {"nombre": "Psicópato", "ruta": "5.jpg"},
            {"nombre": "100 de la de limón en el chevy pop", "ruta": "6.jpg"},
            {"nombre": "Amá, soñé feo", "ruta": "7.jpg"}]
        self.idx_imagen_actual = 0
        self.fichas_img = {}  # Aquí guardaremos los recortes de la imagen

        # --- GESTIÓN DE ESTADOS ---
        self.estado_actual = (1, 2, 3, 4, 0, 5, 6, 7, 8)  # Estado inicial por defecto

        self._construir_interfaz()
        self.cargar_imagen()  # Corta la primera imagen al abrir la app

    def _construir_interfaz(self):

        # Título principal del panel de control
        tk.Label(text="¡Resuelve el Puzzle!", font=("Rockwell", 20, "bold"), fg="#20DF96",
                 bg="#2c3e50").pack(pady=(0, 20))

        frame_top = tk.Frame(self.root, bg="#2c3e50", pady=10)
        frame_top.pack(fill="x")


        frame_herramientas = tk.Frame(frame_top, bg="#2c3e50")
        frame_herramientas.pack(pady=5)

        tk.Button(frame_herramientas, text="Tablero Aleatorio", bg="#8e44ad", fg="white", font=("Rockwell", 12, "bold"),
                  command=self.aplicar_aleatorio).pack(side="left", padx=10, pady=2)
        tk.Button(frame_herramientas, text="Cambiar Imagen", bg="#f39c12", fg="white", font=("Rockwell", 12, "bold"),
                  command=self.cambiar_imagen).pack(side="left", padx=10, pady=2)

        # --- BOTONES DE RESOLUCIÓN ---
        btn_frame = tk.Frame(frame_top, bg="#2c3e50")
        btn_frame.pack(pady=15)
        tk.Button(btn_frame, text="Resolver (BFS)", bg="#27ae60", fg="white", font=("Rockwell", 12, "bold"), width=15,
                  command=lambda: self.iniciar_resolucion('BFS')).pack(side="left", padx=10, pady=2)
        tk.Button(btn_frame, text="Resolver (DFS)", bg="#e74c3c", fg="white", font=("Rockwell", 12, "bold"), width=15,
                  command=lambda: self.iniciar_resolucion('DFS')).pack(side="left", padx=10, pady=2)

        self.lbl_info = tk.Label(self.root, text="¡Mezcla el tablero o cambia la imagen!", bg="#2c3e50", fg="#f1c40f",
                                 font=("Arial", 11, "bold"))
        self.lbl_info.pack(pady=5)

        self.canvas = tk.Canvas(self.root, width=self.canvas_size, height=self.canvas_size, bg="#1a252f",
                                highlightthickness=3, highlightbackground="#ecf0f1")
        self.canvas.pack(pady=20)

        # --- NUEVO: ETIQUETA PARA EL NOMBRE DE LA IMAGEN ---
        self.lbl_nombre_img = tk.Label(self.root, text="Cargando...", bg="#2c3e50", fg="#3498db",
                                       font=("Arial", 16, "bold"))
        self.lbl_nombre_img.pack(pady=(15, 0))

    def aplicar_aleatorio(self):
        if self.is_animating: return
        self.estado_actual = ProblemaPuzzle8.generar_aleatorio()
        self.dibujar_tablero(self.estado_actual)
        self.lbl_info.config(text="Tablero aleatorio generado.", fg="#f1c40f")

    def cambiar_imagen(self):
        if self.is_animating: return
        # Pasamos a la siguiente imagen en la lista de forma cíclica
        self.idx_imagen_actual = (self.idx_imagen_actual + 1) % len(self.catalogo_imagenes)
        self.cargar_imagen()

    def cargar_imagen(self):
        """Abre la imagen completa y la rebana en 9 pedacitos exactos."""
        datos_imagen = self.catalogo_imagenes[self.idx_imagen_actual]
        ruta = datos_imagen["ruta"]
        nombre = datos_imagen["nombre"]

        self.lbl_nombre_img.config(text=f"Rompecabezas: {nombre}")

        self.fichas_img.clear()

        try:
            # Abrimos la imagen y la forzamos a ser del tamaño exacto del canvas (ej. 300x300)
            img_completa = Image.open(ruta).resize((self.canvas_size, self.canvas_size))

            for valor in range(1, 9):  # Fichas del 1 al 8
                # Calculamos en qué coordenadas originales debería ir esta ficha
                pos_correcta = valor - 1
                fila, col = divmod(pos_correcta, 3)
                x1, y1 = col * self.tile_size, fila * self.tile_size
                x2, y2 = x1 + self.tile_size, y1 + self.tile_size

                # 'Recortamos' esa sección geométrica de la imagen
                pedazo = img_completa.crop((x1, y1, x2, y2))
                self.fichas_img[valor] = ImageTk.PhotoImage(pedazo)

            self.dibujar_tablero(self.estado_actual)
            self.lbl_info.config(text=f"{nombre}", fg="#2ecc71")


        except Exception as e:

            messagebox.showwarning("Falta Imagen",
                                   f"No encontré el archivo: '{ruta}'.\nAsegúrate de poner la imagen en la misma carpeta del código.")

            self.dibujar_tablero(self.estado_actual)

    def dibujar_tablero(self, estado):
        self.canvas.delete("all")
        for i, valor in enumerate(estado):
            fila, col = divmod(i, 3)
            x1, y1 = col * self.tile_size, fila * self.tile_size

            if valor == 0:
                # El hueco se queda de color oscuro
                self.canvas.create_rectangle(x1, y1, x1 + self.tile_size, y1 + self.tile_size, fill="#1a252f",
                                             outline="#2c3e50")
            else:
                # Si logramos cargar la imagen, pegamos el pedacito
                if valor in self.fichas_img:
                    self.canvas.create_image(x1, y1, anchor="nw", image=self.fichas_img[valor])
                    # (Opcional) Dibuja el número pequeñito encima para que sea más fácil saber cuál es
                    self.canvas.create_text(x1 + 15, y1 + 15, text=str(valor), font=("Arial", 12, "bold"), fill="white")
                else:
                    # Si no hay imagen, dibujamos el cuadrado clásico azul
                    self.canvas.create_rectangle(x1, y1, x1 + self.tile_size, y1 + self.tile_size, fill="#3498db",
                                                 outline="#2980b9", width=2)
                    self.canvas.create_text(x1 + self.tile_size / 2, y1 + self.tile_size / 2, text=str(valor),
                                            font=("Arial", 30, "bold"), fill="white")

        self.root.update()

    def iniciar_resolucion(self, algoritmo):
        if self.is_animating: return
        self.is_animating = True

        problema = ProblemaPuzzle8(self.estado_actual)
        buscador = BuscadorAlgoritmos(problema)

        self.lbl_info.config(text=f"Calculando con {algoritmo}... (Espere)", fg="#e67e22")
        self.root.update()

        camino, tiempo, memoria = buscador.resolver(algoritmo)

        if not camino:
            self.lbl_info.config(text="Búsqueda fallida.", fg="#e74c3c")
            self.is_animating = False
            return

        self.lbl_info.config(text=f"{algoritmo} | {tiempo:.2f}ms | {memoria:.2f}KB | Pasos: {len(camino) - 1}",
                             fg="#2ecc71")

        for estado in camino:
            self.dibujar_tablero(estado)
            self.estado_actual = estado  # Mantenemos el registro del lugar en el que se quedó
            time.sleep(0.3)

        self.is_animating = False
