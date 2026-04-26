class TicTacToe4x4:
    """
    Clase que representa el estado del juego y sus reglas.
    Actúa como el "tablero físico" donde el algoritmo y el humano interactúan.
    """

    def __init__(self):
        # Crea una matriz de 4 filas por 4 columnas llena de espacios en blanco (' ').
        # Es una lista de listas por su eficiencia y facilidad de indexación board[fila][columna].
        self.board = [[' ' for _ in range(4)] for _ in range(4)]
        self.current_player = 'X'  # Define el jugador inicial por defecto.

    def get_available_moves(self):
        """
        Escanea el tablero y devuelve una lista con las coordenadas vacías.
        IMPORTANCIA PARA LA IA: Esta función genera las "ramas" del árbol de decisiones.
        Cada coordenada vacía devuelta aquí es un posible futuro que Minimax va a explorar.
        """
        moves = []

        # Recorre las 4 filas (r) y las 4 columnas (c)
        for r in range(4):
            for c in range(4):
                # Si encuentra un espacio vacío, guarda su coordenada como una tupla (r, c)
                if self.board[r][c] == ' ':
                    moves.append((r, c))

        return moves

    def make_move(self, row, col, player):
        """
        Ejecuta un movimiento colocando la ficha del jugador ('X' u 'O') en la coordenada indicada.
        En Minimax, esto se usa para simular un paso hacia el futuro.
        """
        self.board[row][col] = player

    def undo_move(self, row, col):
        """
        Deshace un movimiento devolviendo la casilla a su estado vacío (' ').
        IMPORTANCIA PARA LA IA: Esta es la función más importante para la gestión de memoria (Backtracking).
        Permite que la IA use un solo tablero para imaginar millones de futuros,
        poniendo una ficha, evaluando qué pasa, y luego quitándola para probar otra opción,
        evitando así crear copias masivas del tablero en la RAM.
        """
        self.board[row][col] = ' '

    def check_winner(self):
        """
        Verifica todas las líneas posibles de victoria (4 en raya) en el tablero.
        Si alguien completó una línea, devuelve su símbolo ('X' u 'O'). Si nadie ha ganado, devuelve None.
        """

        for i in range(4):
            # 1. Comprueba la Fila 'i'
            # Revisa si la casilla 0 de la fila es igual a la 1, la 2 y la 3, y además se asegura de que no sean espacios vacíos.
            if self.board[i][0] == self.board[i][1] == self.board[i][2] == self.board[i][3] != ' ':
                return self.board[i][0]  # Retorna al ganador de esa fila

            # 2. Comprueba la Columna 'i'
            # Hace exactamente lo mismo, pero iterando sobre el primer índice (la fila) y manteniendo fija la columna 'i'.
            if self.board[0][i] == self.board[1][i] == self.board[2][i] == self.board[3][i] != ' ':
                return self.board[0][i]  # Retorna al ganador de esa columna

        # 3. Comprueba la Diagonal Principal (De arriba-izquierda a abajo-derecha)
        # Casillas: (0,0), (1,1), (2,2), (3,3)
        if self.board[0][0] == self.board[1][1] == self.board[2][2] == self.board[3][3] != ' ':
            return self.board[0][0]

        # 4. Comprueba la Diagonal Secundaria (De arriba-derecha a abajo-izquierda)
        # Casillas: (0,3), (1,2), (2,1), (3,0)
        if self.board[0][3] == self.board[1][2] == self.board[2][1] == self.board[3][0] != ' ':
            return self.board[0][3]

        # Si escanea el tablero y no hay líneas de 4, aún no hay ganador.
        return None

    def is_game_over(self):
        """
        Determina si la partida ha llegado a un Estado Terminal (ya no se puede seguir jugando).
        IMPORTANCIA PARA LA IA: Es el "Caso Base" de la recursividad en Minimax. Le dice al
        algoritmo que ya no tiene sentido seguir buscando más profundo porque el juego terminó.
        """

        # El juego termina si se cumple UNA de dos condiciones:
        # 1. self.check_winner() is not None -> Alguien ya ganó la partida.
        # 2. len(self.get_available_moves()) == 0 -> Ya no hay casillas vacías (Empate).
        return self.check_winner() is not None or len(self.get_available_moves()) == 0