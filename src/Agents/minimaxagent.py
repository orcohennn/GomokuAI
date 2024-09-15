from src.Agents import AgentsUtils
from src.Agents.agent import Agent


class MinimaxAgent(Agent):
    def __init__(self, color, depth=1):
        super().__init__()
        self.depth = depth
        self.color = color

    def get_type(self):
        return 'Minimax'

    def make_move(self, game_state):
        return self.minimax(0, game_state['board'], True)[1]

    def minimax(self, depth, board, maximizingPlayer):

        legal_moves = [(i, j) for i in range(len(board)) for j in range(len(board[0])) if board[i][j] is None]

        if depth == self.depth or self._no_valid_moves(legal_moves):
            return self.evaluation_function(board), (-1, -1)

        if maximizingPlayer:
            return self.max_evaluation(depth, board, legal_moves, maximizingPlayer)

        else:
            return self.min_evaluation(depth, board, legal_moves, maximizingPlayer)

    def max_evaluation(self, depth, board, legal_moves, maximizingPlayer):
        max_eval = -float('inf')
        max_action = (-1, -1)
        for action in legal_moves:
            board_copy = [row[:] for row in board]
            board_copy = self._apply_move(board_copy, action, self.color)

            action_run = self.minimax(depth + 1, board_copy, not maximizingPlayer)

            if action_run[0] > max_eval:
                max_eval = action_run[0]
                max_action = action
        return max_eval, max_action

    def min_evaluation(self, depth, board, legal_moves, maximizingPlayer):
        min_eval = float('inf')
        min_action = (-1, -1)
        for action in legal_moves:
            board_copy = [row[:] for row in board]
            other_color = "white" if self.color == "black" else "black"
            board_copy = self._apply_move(board_copy, action, other_color)

            action_run = self.minimax(depth + 1, board_copy, not maximizingPlayer)

            if action_run[0] < min_eval:
                min_eval = action_run[0]
                min_action = action
        return min_eval, min_action

    def _apply_move(self, board, move, symbol):
        r, c = move
        board[r][c] = symbol
        return board

    def _undo_move(self, board, move):
        r, c = move
        board[r][c] = None

    def _is_winner(self, board, symbol):
        def check_line(r, c, dr, dc):
            """Check for a sequence of five in the given direction."""
            count = 0
            for i in range(5):
                nr = r + i * dr
                nc = c + i * dc
                if 0 <= nr < len(board) and 0 <= nc < len(board[0]) and board[nr][nc] == symbol:
                    count += 1
                else:
                    break
            return count == 5

        for r in range(len(board)):
            for c in range(len(board[0])):
                if board[r][c] == symbol:
                    # Check all directions: right, down, down-right diagonal, down-left diagonal
                    if check_line(r, c, 0, 1) or check_line(r, c, 1, 0) or check_line(r, c, 1, 1) or check_line(r, c, 1,
                                                                                                                -1):
                        return True
        return False

    def _no_valid_moves(self, legal_moves):
        # Check if there are any valid moves left
        return len(legal_moves) == 0

    def is_free(self, board, place):
        i = place[0]
        j = place[1]
        return 0 <= i < len(board) and 0 <= j < len(board[0]) and board[i][j] is None

    def evaluation_function(self, board):
        return AgentsUtils.evaluation_state(board, self.color)
