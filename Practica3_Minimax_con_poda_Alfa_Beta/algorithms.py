import math

class Agente:

    def __init__(self, jugador_ia = 'O', jugador_humano = 'X', profundidad_maxima = 3):

        self.ia = jugador_ia
        self.humano = jugador_humano
        self.profundidad_maxima = profundidad_maxima
        self.nodos_explorados = 0

    def evaluar_tablero(self, model):

        """
            Función Heurística Estática.
            Evalúa el estado actual del tablero y le asigna un puntaje numérico.
            Valores positivos altos favorecen a la IA (Maximizador).
            Valores negativos altos favorecen al Humano (Minimizador).
            """

        # ---------------------------------------------------------
        # 1. EVALUACIÓN DE ESTADOS TERMINALES (Fin del juego)
        # ---------------------------------------------------------

        ganador = model.check_winner()

        # Si la IA gana, se retorna un valor arbitrariamente alto (equivalente a "infinito positivo").
        # Minimax siempre elegirá el camino que lleve a este 10000.
        if ganador == self.ia:
            return 10000

        # Si el humano gana, se retorna un valor "infinito negativo".
        # La IA evitará a toda costa cualquier rama del árbol que termine en este -10000.
        if ganador == self.humano:
            return -10000

        # Si el tablero está lleno y no hay ganador, es un empate absoluto.
        # El puntaje es neutro (0).
        if ganador is None and len(model.get_available_moves()) == 0:
            return 0

        # ---------------------------------------------------------
        # 2. EVALUACIÓN HEURÍSTICA (Estados intermedios)
        # ---------------------------------------------------------
        # Si el juego no ha terminado, calculamos un puntaje basado en el potencial del tablero.
        score = 0

        lineas = []

        # --- EXTRACCIÓN DE VÍAS DE VICTORIA ---
        # En un tablero 4x4, existen 10 formas de ganar (4 filas, 4 columnas, 2 diagonales).
        # Este bloque agrupa todas esas combinaciones en una sola lista de listas para evaluarlas fácilmente.
        for i in range(4):
            # Añade la fila 'i' completa
            lineas.append([model.board[i][j] for j in range(4)])
            # Añade la columna 'i' completa
            lineas.append([model.board[j][i] for j in range(4)])

        # Añade la diagonal principal (de arriba-izquierda a abajo-derecha)
        lineas.append([model.board[i][i] for i in range(4)])
        # Añade la diagonal secundaria (de arriba-derecha a abajo-izquierda)
        lineas.append([model.board[i][3 - i] for i in range(4)])

        # --- ANÁLISIS DE CADA LÍNEA ---
        for linea in lineas:
            # Contamos cuántas fichas tiene cada jugador y cuántos espacios vacíos hay en la línea actual.
            contador_ia = linea.count(self.ia)
            contador_humano = linea.count(self.humano)
            contador_vacio = linea.count(' ')

            # DECISIÓN DE DISEÑO: Escala Exponencial (10^n)
            # Se usa una potencia de 10 para crear una prioridad absoluta.
            # Tener 3 fichas en línea (10^3 = 1000 pts) es muchísimo más valioso
            # que tener tres líneas diferentes con 2 fichas (10^2 * 3 = 300 pts).
            # Esto enseña a la IA a priorizar terminar líneas antes que dispersarse.

            # A) Recompensar líneas ofensivas de la IA (solo si el humano no ha bloqueado)
            if contador_ia > 0 and contador_humano == 0:
                score += (10 ** contador_ia)

            # B) Penalizar líneas peligrosas del humano (solo si la IA no las ha bloqueado)
            elif contador_humano > 0 and contador_ia == 0:
                score -= (10 ** contador_humano)

            # DECISIÓN DE DISEÑO: Sistema de Amenazas Inminentes
            # Un tablero 4x4 es muy amplio, por lo que las interrupciones en el turno 3 son críticas.

            # C) Recompensa por bloquear con éxito
            # Si la línea tiene 3 fichas del humano, pero la IA puso 1 ficha, significa que la IA bloqueó el 4 en raya.
            # Se otorgan 500 puntos para "felicitar" a la IA por esta acción defensiva vital.
            if contador_humano == 3 and contador_ia == 1:
                score += 500

                # D) Penalización por amenaza letal
            # Si el humano tiene 3 fichas y hay 1 espacio vacío, el humano ganará en el próximo turno.
            # Se restan 1000 puntos. Este valor es tan negativo que obligará al algoritmo Minimax
            # a retroceder en el árbol y buscar una jugada que bloquee este escenario a toda costa.
            if contador_humano == 3 and contador_vacio == 1:
                score -= 1000

        # ---------------------------------------------------------
        # 3. EVALUACIÓN POSICIONAL (Control del Tablero)
        # ---------------------------------------------------------
        # Las casillas centrales (1,1), (1,2), (2,1) y (2,2) son estadísticamente las más valiosas
        # porque cruzan más líneas ganadoras (filas, columnas y ambas diagonales).
        center_positions = [(1, 1), (1, 2), (2, 1), (2, 2)]

        for r, c in center_positions:
            # Se otorga un pequeño bono (+25) por dominar el centro. Es un valor bajo comparado
            # con las amenazas reales, útil principalmente al inicio del juego (aperturas)
            # cuando el tablero está muy vacío y la IA no sabe dónde tirar.
            if model.board[r][c] == self.ia:
                score += 25

            # De igual forma, se penaliza si el humano toma el centro.
            elif model.board[r][c] == self.humano:
                score -= 25

        # Finalmente, se retorna el balance total del estado actual del tablero.
        return score

    def minimax(self, model, depth, is_maximizing):
        """
        Algoritmo Minimax puro.
        Explora todas las jugadas posibles hasta una profundidad máxima y retorna
        la mejor jugada junto con su puntaje evaluado.
        """

        # 1. MÉTRICA DE RENDIMIENTO
        # Cada vez que se llama a esta función, significa que entramos a analizar
        # un nuevo estado del tablero (un nodo en el árbol de decisiones).
        self.nodos_explorados += 1

        # 2. CASO BASE (Condición de parada de la recursión)
        # El algoritmo se detiene si alcanza el límite de profundidad (depth == 0)
        # o si el juego ya terminó en este escenario simulado (victoria, derrota o empate).
        if depth == 0 or model.is_game_over():
            # Si se detiene, llama a la función heurística para calificar este tablero
            # y no retorna ninguna jugada (None) porque ya no hay movimientos a realizar.
            return self.evaluar_tablero(model), None

        # Obtiene todas las casillas vacías donde se puede tirar.
        moves = model.get_available_moves()
        best_move = None

        # ---------------------------------------------------------
        # 3. TURNO DE LA IA (Maximizador)
        # ---------------------------------------------------------
        if is_maximizing:
            # Inicializa la mejor evaluación posible en el valor más bajo (infinito negativo).
            # Cualquier puntaje real será mayor que esto, por lo que se actualizará rápido.
            max_eval = -math.inf

            for move in moves:
                # a) SIMULAR EL MOVIMIENTO
                # Pone una ficha de la IA en la casilla actual.
                model.make_move(move[0], move[1], self.ia)

                # b) RECURSIÓN
                # Llama a minimax de nuevo pero restando 1 a la profundidad.
                # Cambia is_maximizing a False porque el siguiente turno simulado es del humano.
                eval_score, _ = self.minimax(model, depth - 1, False)

                # c) BACKTRACKING (Deshacer el movimiento)
                # ¡CRUCIAL! Quita la ficha que acaba de poner para dejar el tablero
                # exactamente como estaba, y poder simular el siguiente movimiento del ciclo 'for'.
                model.undo_move(move[0], move[1])

                # d) ACTUALIZAR EL MEJOR RESULTADO
                # Si el puntaje que devolvió ese futuro imaginario es mejor (más alto)
                # que el que teníamos, lo guardamos como nuestro nuevo mejor movimiento.
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move

            # Al terminar de revisar todas las opciones, retorna el puntaje máximo y la jugada.
            return max_eval, best_move


        # ---------------------------------------------------------
        # 4. TURNO DEL HUMANO (Minimizador)
        # ---------------------------------------------------------
        else:
            # Inicializa la evaluación en el valor más alto (infinito positivo).
            # Asume que el humano siempre buscará el puntaje más bajo posible (hacer perder a la IA).
            min_eval = math.inf

            for move in moves:

                # a) SIMULAR EL MOVIMIENTO
                # Pone una ficha del Humano en la casilla actual.
                model.make_move(move[0], move[1], self.humano)

                # b) RECURSIÓN
                # Vuelve a llamar a minimax restando profundidad.
                # Cambia is_maximizing a True porque el siguiente turno volverá a ser de la IA.
                eval_score, _ = self.minimax(model, depth - 1, True)

                # c) BACKTRACKING
                # Deshace la jugada simulada del humano.
                model.undo_move(move[0], move[1])

                # d) ACTUALIZAR EL PEOR RESULTADO
                # La IA asume que el humano elegirá la jugada que le haga más daño (el puntaje menor).
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move

            # Retorna el puntaje más bajo que el humano lograría forzar y qué jugada llevaría a ello.
            return min_eval, best_move

    def minimax_alpha_beta(self, model, depth, alpha, beta, is_maximizing):
        self.nodos_explorados += 1

        if depth == 0 or model.is_game_over():
            return self.evaluar_tablero(model), None

        moves = model.get_available_moves()
        best_move = None

        if is_maximizing:
            max_eval = -math.inf
            for move in moves:
                model.make_move(move[0], move[1], self.ia)
                eval_score, _ = self.minimax_alpha_beta(model, depth - 1, alpha, beta, False)
                model.undo_move(move[0], move[1])

                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move

                alpha = max(alpha, eval_score)

                if beta <= alpha:
                    break  # Poda Alfa-Beta

            return max_eval, best_move

        else:
            min_eval = math.inf
            for move in moves:
                model.make_move(move[0], move[1], self.humano)
                eval_score, _ = self.minimax_alpha_beta(model, depth - 1, alpha, beta, True)
                model.undo_move(move[0], move[1])

                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move

                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # Poda Alfa-Beta
            return min_eval, best_move