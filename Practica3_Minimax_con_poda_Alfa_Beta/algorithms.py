import math

class Agent:
    def __init__(self, ai_player='O', human_player='X', max_depth=3):
        self.ai = ai_player
        self.human = human_player
        self.max_depth = max_depth
        self.nodes_explored = 0

    def evaluate_board(self, model):
        winner = model.check_winner()
        if winner == self.ai: return 10000
        if winner == self.human: return -10000
        if winner is None and len(model.get_available_moves()) == 0: return 0

        score = 0
        lines = []
        # Extraer filas y columnas
        for i in range(4):
            lines.append([model.board[i][j] for j in range(4)])
            lines.append([model.board[j][i] for j in range(4)])
        # Extraer diagonales
        lines.append([model.board[i][i] for i in range(4)])
        lines.append([model.board[i][3 - i] for i in range(4)])

        for line in lines:
            ai_count = line.count(self.ai)
            human_count = line.count(self.human)
            empty_count = line.count(' ')

            # 1. Fichas propias en líneas abiertas
            if ai_count > 0 and human_count == 0:
                score += (10 ** ai_count)
            # Penalización si el humano tiene líneas abiertas
            elif human_count > 0 and ai_count == 0:
                score -= (10 ** human_count)

            # 2. Bloqueo de líneas del oponente con 3 fichas
            if human_count == 3 and ai_count == 1:
                score += 500  # Bonificación por haber bloqueado una amenaza inminente
            if human_count == 3 and empty_count == 1:
                score -= 1000  # Amenaza crítica en el tablero

        # 3. Control del centro del tablero
        center_positions = [(1, 1), (1, 2), (2, 1), (2, 2)]
        for r, c in center_positions:
            if model.board[r][c] == self.ai:
                score += 25
            elif model.board[r][c] == self.human:
                score -= 25

        return score

    def minimax(self, model, depth, is_maximizing):
        self.nodes_explored += 1

        if depth == 0 or model.is_game_over():
            return self.evaluate_board(model), None

        moves = model.get_available_moves()
        best_move = None

        if is_maximizing:
            max_eval = -math.inf
            for move in moves:
                model.make_move(move[0], move[1], self.ai)
                eval_score, _ = self.minimax(model, depth - 1, False)
                model.undo_move(move[0], move[1])

                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move
            return max_eval, best_move
        else:
            min_eval = math.inf
            for move in moves:
                model.make_move(move[0], move[1], self.human)
                eval_score, _ = self.minimax(model, depth - 1, True)
                model.undo_move(move[0], move[1])

                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move
            return min_eval, best_move

    def minimax_alpha_beta(self, model, depth, alpha, beta, is_maximizing):
        self.nodes_explored += 1

        if depth == 0 or model.is_game_over():
            return self.evaluate_board(model), None

        moves = model.get_available_moves()
        best_move = None

        if is_maximizing:
            max_eval = -math.inf
            for move in moves:
                model.make_move(move[0], move[1], self.ai)
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
                model.make_move(move[0], move[1], self.human)
                eval_score, _ = self.minimax_alpha_beta(model, depth - 1, alpha, beta, True)
                model.undo_move(move[0], move[1])

                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move

                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # Poda Alfa-Beta
            return min_eval, best_move