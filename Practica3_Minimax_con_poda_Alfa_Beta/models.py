class TicTacToe4x4:

    def __init__(self):

        self.board = [[' ' for _ in range(4)] for _ in range(4)]
        self.current_player = 'X'  # El humano es 'X', la IA es 'O'

    def get_available_moves(self):

        moves = []

        for r in range(4):
            for c in range(4):

                if self.board[r][c] == ' ':

                    moves.append((r, c))

        return moves

    def make_move(self, row, col, player):
        self.board[row][col] = player

    def undo_move(self, row, col):
        self.board[row][col] = ' '

    def check_winner(self):
        # Filas y Columnas
        for i in range(4):
            if self.board[i][0] == self.board[i][1] == self.board[i][2] == self.board[i][3] != ' ':
                return self.board[i][0]

            if self.board[0][i] == self.board[1][i] == self.board[2][i] == self.board[3][i] != ' ':
                return self.board[0][i]

        # Diagonales
        if self.board[0][0] == self.board[1][1] == self.board[2][2] == self.board[3][3] != ' ':
            return self.board[0][0]

        if self.board[0][3] == self.board[1][2] == self.board[2][1] == self.board[3][0] != ' ':
            return self.board[0][3]

        return None

    def is_game_over(self):
        return self.check_winner() is not None or len(self.get_available_moves()) == 0