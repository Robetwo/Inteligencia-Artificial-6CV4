import tkinter as tk
from tkinter import ttk, messagebox
import time

from modelo import ProblemaJarras
from algoritmos import BuscadorAlgoritmos


class InterfazJarras:

    def __init__(self, root):
        # 1. Configuración de la Ventana Maestra (root)
        self.root = root
        self.root.title("Inteligencia Artificial - Problema de las Jarras")
        self.root.geometry("780x630")
        self.root.configure(bg="#f0f2f5")  # Color de fondo gris claro

        # Diccionario de tipografías

        self.fuente_titulo = ("Segoe UI", 18, "bold")
        self.fuente_subtitulo = ("Segoe UI", 12, "bold")
        self.fuente_normal = ("Segoe UI", 11)
        self.fuente_codigo = ("Consolas", 10)

        self._construir_interfaz()

    def _construir_interfaz(self):
        # --- TÍTULO PRINCIPAL ---
        lbl_titulo = tk.Label(self.root, text="Búsqueda de Estados: Jarras de Agua", font=self.fuente_titulo,
                              bg="#f0f2f5", fg="#2c3e50")
        lbl_titulo.pack(pady=(5, 5))

        # --- 1. SECCIÓN DE CONFIGURACIÓN ---
        # LabelFrame agrupa visualmente los controles con un pequeño borde y título.
        frame_config = tk.LabelFrame(self.root, text="Configuración del Problema", font=self.fuente_subtitulo,
                                     bg="#f0f2f5", fg="#34495e", padx=20, pady=15)
        frame_config.pack(fill="x", padx=30, pady=10)

        # PREVENCIÓN DE ERRORES: Usamos Spinbox en lugar de un cuadro de texto (Entry) normal.
        # Porque un Spinbox obliga al usuario a elegir números con flechitas.
        # Esto evita que alguien escriba letras como "Hola" y haga colapsar el programa.
        tk.Label(frame_config, text="Capacidad Jarra 1:", font=self.fuente_normal, bg="#f0f2f5").grid(row=0, column=0,
                                                                                                      padx=5, pady=5,
                                                                                                      sticky="e")
        self.spin_cap1 = ttk.Spinbox(frame_config, from_=1, to=100, width=8, font=self.fuente_normal)
        self.spin_cap1.set(4)  # Valor por defecto del problema
        self.spin_cap1.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame_config, text="Capacidad Jarra 2:", font=self.fuente_normal, bg="#f0f2f5").grid(row=0, column=2,
                                                                                                      padx=5, pady=5,
                                                                                                      sticky="e")
        self.spin_cap2 = ttk.Spinbox(frame_config, from_=1, to=100, width=8, font=self.fuente_normal)
        self.spin_cap2.set(3)
        self.spin_cap2.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(frame_config, text="Objetivo (Litros):", font=self.fuente_normal, bg="#f0f2f5").grid(row=0, column=4,
                                                                                                      padx=5, pady=5,
                                                                                                      sticky="e")
        self.spin_obj = ttk.Spinbox(frame_config, from_=1, to=100, width=8, font=self.fuente_normal)
        self.spin_obj.set(2)
        self.spin_obj.grid(row=0, column=5, padx=5, pady=5)

        # --- 2. SECCIÓN DE ACCIONES  ---
        frame_botones = tk.Frame(self.root, bg="#f0f2f5")
        frame_botones.pack(pady=10)

        # Los botones usan 'lambda' para pasarle un argumento ('BFS' o 'DFS') a la misma función.
        # Esto evita tener que crear dos funciones separadas.
        btn_bfs = tk.Button(frame_botones, text="Resolver con BFS (Amplitud)",
                            font=self.fuente_subtitulo, bg="#2ecc71", fg="white",
                            activebackground="#27ae60", activeforeground="white",
                            cursor="hand2", padx=15, pady=8, relief="flat",
                            command=lambda: self.ejecutar_busqueda('BFS'))
        btn_bfs.grid(row=0, column=0, padx=5)

        btn_dfs = tk.Button(frame_botones, text="Resolver con DFS (Profundidad)",
                            font=self.fuente_subtitulo, bg="#3498db", fg="white",
                            activebackground="#2980b9", activeforeground="white",
                            cursor="hand2", padx=15, pady=8, relief="flat",
                            command=lambda: self.ejecutar_busqueda('DFS'))
        btn_dfs.grid(row=0, column=1, padx=5)

        # --- 3. SECCIÓN DE RESULTADOS Y ANIMACIÓN  ---
        frame_resultados = tk.LabelFrame(self.root, text="Resultados", font=self.fuente_subtitulo, bg="#f0f2f5",
                                         fg="#34495e", padx=10, pady=-10)
        frame_resultados.pack(fill="both", expand=True, padx=30, pady=2)

        self.label_resultados = tk.Label(frame_resultados, text="Ingresa los valores y selecciona un algoritmo...",
                                         font=("Segoe UI", 11, "italic"), bg="#f0f2f5", fg="#7f8c8d")
        self.label_resultados.pack(pady=(0, 10))

        # Cuadro de texto con barra de desplazamiento para ver el historial de coordenadas.
        frame_texto = tk.Frame(frame_resultados)
        frame_texto.pack(pady=1, fill="x")
        scroll = tk.Scrollbar(frame_texto)
        scroll.pack(side="right", fill="y")
        self.texto_pasos = tk.Text(frame_texto, height=4, font=self.fuente_codigo, yscrollcommand=scroll.set,
                                   bg="#ffffff", relief="solid", borderwidth=1)
        self.texto_pasos.pack(side="left", fill="x", expand=True)
        scroll.config(command=self.texto_pasos.yview)

        # El Canvas muestra los vectores geométricos.
        self.canvas = tk.Canvas(frame_resultados, width=450, height=250, bg="#ffffff", highlightthickness=1,
                                highlightbackground="#bdc3c7")
        self.canvas.pack(pady=5)

        # Pinta la pantalla inicial con jarras vacías.
        self.dibujar_estado(0, 4, 0, 3)

    def dibujar_estado(self, val1, cap1, val2, cap2):
        """
        Recibe cuánta agua hay (val) y de qué tamaño es la jarra (cap).
        Convierte esa matemática abstracta en rectángulos en la pantalla.
        """
        # Borra el fotograma anterior para dibujar el nuevo (efecto de animación).
        self.canvas.delete("all")

        # Variables espaciales: 'suelo' es el eje Y inferior. 'x1' y 'x2' son los ejes X de cada jarra.
        suelo, ancho, x1, x2 = 220, 70, 120, 270

        # 'escala_max' nos permite saber cuál es la jarra más grande para dibujarla más alta visualmente,
        # manteniendo una proporción realista entre ambas.
        escala_max = max(cap1, cap2) or 1

        # Mapeamos los litros reales a píxeles de pantalla (máximo 160 píxeles de alto).
        alto_j1 = (cap1 / escala_max) * 160
        alto_j2 = (cap2 / escala_max) * 160

        # Regla de 3 simple: ¿Si 'cap' son 'alto' píxeles, cuántos píxeles son 'val' litros?
        agua_j1 = (val1 / cap1) * alto_j1 if cap1 > 0 else 0
        agua_j2 = (val2 / cap2) * cap2 if cap2 > 0 else 0

        # 1. Pintamos el agua (rectángulos azules que crecen desde el suelo hacia arriba).
        # Nota: En los Canvas de computadoras, la coordenada Y=0 está ARRIBA, por eso restamos al suelo.
        self.canvas.create_rectangle(x1, suelo - agua_j1, x1 + ancho, suelo, fill="#3498db", outline="#2980b9")
        self.canvas.create_rectangle(x2, suelo - agua_j2, x2 + ancho, suelo, fill="#3498db", outline="#2980b9")

        # 2. Pintamos el contorno de cristal (solo las líneas exteriores, huecas por dentro).
        self.canvas.create_rectangle(x1, suelo - alto_j1, x1 + ancho, suelo, outline="#34495e", width=4)
        self.canvas.create_rectangle(x2, suelo - alto_j2, x2 + ancho, suelo, outline="#34495e", width=4)

        # 3. Pintamos los textos decorativos e informativos.
        self.canvas.create_text(x1 + ancho / 2, suelo - alto_j1 - 15, text="Jarra 1", font=("Segoe UI", 10, "bold"),
                                fill="#2c3e50")
        self.canvas.create_text(x2 + ancho / 2, suelo - alto_j2 - 15, text="Jarra 2", font=("Segoe UI", 10, "bold"),
                                fill="#2c3e50")
        self.canvas.create_text(x1 + ancho / 2, suelo + 15, text=f"{val1} / {cap1} L", font=("Segoe UI", 11))
        self.canvas.create_text(x2 + ancho / 2, suelo + 15, text=f"{val2} / {cap2} L", font=("Segoe UI", 11))

        # OBLIGA a Tkinter a repintar la pantalla inmediatamente.
        # Sin esto, Tkinter esperaría a que acabe toda la función para dibujar, perdiendo la animación.
        self.root.update()

    def ejecutar_busqueda(self, algoritmo):
        """
        Recoge los datos visuales, despierta al cerebro matemático, y procesa la respuesta.
        """
        try:
            # Extracción de datos.
            # Los Spinbox devuelven texto (Strings), así que los forzamos a ser enteros (int).
            c1, c2, obj = int(self.spin_cap1.get()), int(self.spin_cap2.get()), int(self.spin_obj.get())
        except ValueError:
            # Si el usuario logró meter una letra, atrapamos el error y evitamos que el programa explote.
            messagebox.showerror("Error de entrada", "Por favor, utiliza los selectores para ingresar números enteros.")
            return

        # Conectamos los módulos lógicos
        problema = ProblemaJarras(c1, c2, obj)
        buscador = BuscadorAlgoritmos(problema)

        self.label_resultados.config(text=f"Calculando solución con {algoritmo}...", fg="#e67e22")
        self.root.update()

        # 3. Ejecución del motor lógico
        camino, tiempo, memoria = buscador.resolver(algoritmo)

        # Si el motor devuelve None (porque es_posible() dio Falso, o se quedó sin opciones).
        if not camino:
            messagebox.showwarning("Sin solución",
                                   f"Es matemáticamente imposible alcanzar {obj} L con jarras de {c1} L y {c2} L.")
            self.label_resultados.config(text="Búsqueda terminada: Sin solución.", fg="#e74c3c")
            return

        # 4. Formateo de Resultados
        resultado_txt = f"({algoritmo}) | Tiempo: {tiempo:.4f} ms | Memoria: {memoria:.2f} KB | Pasos: {len(camino) - 1}"
        self.label_resultados.config(text=resultado_txt, fg="#27ae60", font="bold")

        # Limpiamos el historial de texto y escribimos la nueva ruta.
        self.texto_pasos.delete(1.0, tk.END)
        rutas_formateadas = " ➔ ".join([f"({x},{y})" for x, y in camino])
        self.texto_pasos.insert(tk.END, rutas_formateadas)

        # 5. El Bucle de Animación
        for x, y in camino:
            self.dibujar_estado(x, c1, y, c2)
            # Pausa el código 0.6 segundos antes de dibujar el siguiente fotograma.
            # (Nota técnica: time.sleep 'congela' la app entera, pero self.root.update() en
            # dibujar_estado lo parcha para que al menos actualice los píxeles).
            time.sleep(0.6)
